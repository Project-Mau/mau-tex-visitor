# Mau TeX Visitor

This is a plugin for the [Mau](https://github.com/Project-Mau/mau) markup language. The plugin provides the conversion from Mau source to TeX.

You can install this plugin with

```
pip install mau-tex-visitor
```

and Mau will automatically be able to load it. To use the visitor you need to load it and to pass it to the class `Mau` when you instantiate it

``` python
from mau import Mau, load_visitors
from mau.message import LogMessageHandler

visitor_classes = load_visitors()

visitors = {i.format_code: i for i in visitor_classes.values()}
visitor_class = visitors["tex"]

message_handler = LogMessageHandler()

mau = Mau(message_handler)

result = mau.process(visitor_class, text, "source.mau")
```

The default extension for templates is `.tex`.
