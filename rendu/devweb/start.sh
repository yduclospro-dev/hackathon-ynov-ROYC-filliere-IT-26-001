#!/bin/bash
echo "Lancement de l'interface de chat TechCorp Industries..."
if command -v xdg-open > /dev/null; then
  xdg-open index.html
elif command -v open > /dev/null; then
  open index.html
else
  echo "Veuillez ouvrir index.html manuellement dans votre navigateur."
fi
