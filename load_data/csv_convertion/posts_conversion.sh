for file in xml/Posts0*; do
mv "$file" "xml/Posts.xml"
docker compose up
mv "xml/Posts.xml" "$file"
mv "csv/Posts.csv" "csv/$(basename ${file%.xml}).csv"; done
