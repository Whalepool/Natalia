# Natalia Plugins  

### To Create a new plugin
#### 1
```bash
cd plugins 
cp -r blank my_new_plugin_name
vim my_new_plugin_name/__init__.py 
```
#### 2
Edit your new plugin class name.  
Make sure the `run` function is executing this class name

#### 3
Next add your plugin to the config yaml file to enable natalia to load it 
```
plugins:

  ...

  ...  

  ################################
  # Load my  new plugin here
  ################################
  - 
    name: 'my_plugin_folder_name'
    data: 

```
#### 4
Next edit/setup your plugin config checker in your plugin __init__.py file
```python
check_config_integrity()
```