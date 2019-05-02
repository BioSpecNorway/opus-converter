SET python_path="C:/miniconda3/python"
SET converter_path="%userprofile%/Desktop/opus-converter/opus_converter.py"

%python_path% %converter_path% . --format csv --split --onefile --save-inplace --verbose 

pause