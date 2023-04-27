. base.sh
#graphql '{"query":"{__schema{ queryType{fields{name description}}  }}"}'
#graphql '{"query":"{__schema{  queryType{fields{name}} directives{name description locations } }}"}'
#graphql '{"query":"{__schema{ queryType{fields{name}} types{name description} }}"}'

graphql '{"query":"{__schema{ queryType{fields{name }}  }}"}'
echo
graphql '{"query":"{__schema{ types{name fields{name}} }}"}'