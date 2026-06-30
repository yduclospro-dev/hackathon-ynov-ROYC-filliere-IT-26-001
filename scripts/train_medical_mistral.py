# -*- coding: utf-8 -*-
"""
Mistral 7B Medical Fine-Tuning Script
Perform QLoRA fine-tuning on Mistral-7B-Instruct for medical chat applications
"""

import os
import torch
import json
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer, 
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from datasets import load_dataset

class MedicalMistralTrainer:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.3", dataset_name="ruslanmv/ai-medical-chatbot"):
        """
        Initialize the medical fine-tuning trainer for Mistral 7B.
        """
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.tokenizer = None
        self.model = None

    def setup_model(self):
        """Load Mistral 7B model with memory-efficient QLoRA configuration"""
        print(f"Loading base model: {self.model_name}")

        # Load tokenizer with Mistral configuration
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

        # QLoRA 4-bit config for Colab GPU (T4/L4/A100)
        if torch.cuda.is_available():
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            print("4-bit quantization enabled for GPU training")
        else:
            quantization_config = None
            print("Running in CPU mode (Warning: training will be extremely slow!)")

        model_kwargs = {
            "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
        }

        if quantization_config:
            model_kwargs["quantization_config"] = quantization_config
            model_kwargs["device_map"] = "auto"

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            **model_kwargs
        )

        if not quantization_config and torch.cuda.is_available():
            self.model = self.model.cuda()

        if quantization_config:
            self.model = prepare_model_for_kbit_training(self.model)

        # LoRA Configuration adapted specifically to Mistral architecture
        # Target modules MUST target q_proj, k_proj, v_proj instead of qkv_proj
        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )

        self.model = get_peft_model(self.model, lora_config)
        print(f"Model PEFT initialization complete. Trainable parameters: {self.model.num_parameters()}")

    def load_and_format_data(self):
        """Download and format the medical dataset using Mistral [INST] template"""
        print(f"Loading medical dataset from HF: {self.dataset_name}")
        
        # Load dataset from Hugging Face
        raw_dataset = load_dataset(self.dataset_name, split="train")
        
        # Take a subset if resources are limited (e.g. 5000 examples for quick fine-tuning)
        subset_size = min(5000, len(raw_dataset))
        raw_dataset = raw_dataset.select(range(subset_size))
        print(f"Selected subset of {subset_size} medical examples")

        # Format dataset using Mistral official Chat template:
        # <s>[INST] User prompt [/INST] Bot response </s>
        def format_prompt(example):
            patient_query = example.get("Patient", "").strip()
            doctor_response = example.get("Doctor", "").strip()
            
            # Format using Mistral official syntax
            formatted_text = f"<s>[INST] {patient_query} [/INST] {doctor_response} </s>"
            return {"text": formatted_text}

        formatted_dataset = raw_dataset.map(format_prompt, remove_columns=raw_dataset.column_names)
        return formatted_dataset

    def tokenize_dataset(self, dataset):
        """Tokenize formatted text for language modeling"""
        print("Tokenizing medical dataset...")

        def tokenize_function(examples):
            tokenized = self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=512,
                return_tensors="pt"
            )
            tokenized["labels"] = tokenized["input_ids"].clone()
            return tokenized

        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]
        )
        return tokenized_dataset

    def train(self, tokenized_dataset, output_dir="./medical_mistral_lora", epochs=2):
        """Run the training loop"""
        print("Initializing SFT training arguments...")

        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            warmup_steps=100,
            logging_steps=20,
            save_steps=200,
            save_total_limit=2,
            remove_unused_columns=False,
            dataloader_drop_last=True,
            no_cuda=not torch.cuda.is_available(),
            fp16=torch.cuda.is_available(),
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )

        print("Starting training loop...")
        trainer.train()
        
        # Save fine-tuned LoRA weights
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        print(f"Training finished! Model saved to {output_dir}")

    def run_pipeline(self):
        self.setup_model()
        formatted_data = self.load_and_format_data()
        tokenized_data = self.tokenize_dataset(formatted_data)
        self.train(tokenized_data)

if __name__ == "__main__":
    # This script is meant to be run in Google Colab with GPU acceleration
    trainer = MedicalMistralTrainer()
    trainer.run_pipeline()
