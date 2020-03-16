if [ ! -d "lib" ];
then
    mkdir lib
fi

if [ ! -f "lib/swagger-codegen-cli.jar" ];
then
    wget http://central.maven.org/maven2/io/swagger/swagger-codegen-cli/2.2.2/swagger-codegen-cli-2.2.2.jar -O lib/swagger-codegen-cli.jar
fi

echo "##############################################"
echo "# to run the code generator                  #"
echo "#                                            #"
echo "# java -jar lib/swagger-codegen-cli.jar help #"
echo "#                                            #"
echo "##############################################"

echo "https://github.com/swagger-api/swagger-codegen?ref=producthunt#overview"

langs=(java javascript python html dynamic-html)
for l in "${langs[@]}"
do
   mkdir -p bindings/$l
   echo java -jar lib/swagger-codegen-cli.jar generate -i swagger.yaml -l $l -o bindings/$l
   java -jar lib/swagger-codegen-cli.jar generate -i swagger.yaml -l $l -o bindings/$l
done
