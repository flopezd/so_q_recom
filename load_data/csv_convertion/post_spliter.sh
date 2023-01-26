split -n l/10 -d --additional-suffix=.xml Posts.xml Posts

for file in Posts0*; do
if [ $file != Posts00.xml ];
then
sed -i '1i\
<?xml version="1.0" encoding="utf-8"?>
1i\
<posts>
' $file
fi
if [ $file != Posts09.xml ];
then
echo '</posts>' >> $file
fi; done
