To format a prompt template, I used format_map(). This formats a dict into the placeholders of the tempalte.

However, in our prompt we have curly braces that should not be formated, since they are from example dictionaries.

To replace only the placeholders and not change the example dictionaries, I am temporarily replacing all  "{ and }" with < and >

# Temporary replace
modified_str = template.replace('{\",'<').replace('\"}','>') 

# Map
str_with_map = modified_str.format_map(data)

# Return to example dict
final_string = str_with_map.replace('<','{\"').replace('>','\"}')


When building a prompt, make sure that all example dicts have their { and  } symbols next to a double quote
"example_key": {"example_value"}


And, when defining a value to replace, make sure that it does not have any single quotes next to it

{example_placeholder}