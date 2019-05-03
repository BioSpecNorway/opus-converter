# Opus converter

Script which helps to gather a folder of .0 files into a mat, csv or npy file.
At this time it saves only AB section (raw spectra).

### Requirements

Python 3
```
pip install numpy scipy pandas opusFC
```

### Quick reference

```
usage: opus_converter.py [-h] [-f {mat,csv,npy}] [-one] [-s] [-sep SEPARATOR]
                         [-depth SEARCH_DEPTH] [--debug] [-v]
                         [-out OUTPUT_DIRECTORY] [-i]
                         directory

Utility for converting files from OPUS format .0 to .mat;.csv;.npy

positional arguments:
  directory             Directory where to start the search

optional arguments:
  -h, --help            show this help message and exit
  -f {mat,csv,npy}, --format {mat,csv,npy}
  -one, --onefile       Pack all information into one csv file (doesn't work
                        with another formats)
  -s, --split           Splits sample name with --separator into columns
  -fix, --fix-table     fixes table after splitting by inserting empty cells
  -sep SEPARATOR, --separator SEPARATOR
                        separator which used to split sample name if --split
                        is used
  -depth SEARCH_DEPTH, --search-depth SEARCH_DEPTH
  --debug
  -q, --quiet
  -out OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
  -i, --save-inplace    save result files in folder with spectra
  -u, --update          rewrites files which already exist
```

### Examples

```bash
python opus_converter.py .
python opus_converter.py ./my_experiments

# for windows, %userprofile% is a windows variable for the current user folder
# this will find all .0 in folder C:\\Users\\current_user\\my_experiments and 
# save results into folder C:\\Users\\current_user\\my_experiments\\converted
# the maximum depth of search 3 folders.
python opus_converter.py "%USERPROFILE%/my_experiments" -out "%USERPROFILE%/my_experiments/converted"

# This will convert into one .csv file and also will split the name of file with 
# separator _
python opus_converter.py . -f csv --onefile --split
```

# Explanation

In order to run script you should write `python opus_converter.py start_folder`. Where start_folder is a folder 
where search will start. If you want to start it in current directory you can just type . (point), that usually means 
current directory.

By default it doesn't go deeper than 3 folders. You can change the depth of search by passing parameter `-depth n`.
By default it will convert into ont .mat file. You can select a format by passing parameter `-f format`, where format 
can be mat, csv or npy. 

Csv is the format that can be read by Excel. By default it will create 3 separate files for each folder: spectra.csv, 
labels.csv, wavenumbers.csv. In order to get all information in one file pass parameter `-one` or `--onefile`.

By default it creates only one column called `sample_name` in which it stores the name of .0 file with spectrum. 
It is also possible to automatically split the name of sample into another columns, e.g. `Exp1_apple_3ml` will be splitted
into 3 columns `Exp1`, `apple`, `3ml`, with names column0, column1, column2. If you want to enable split option then you
need to pass `-s` or `--split`. You can also specify a separator by passing parameter `-sep _` or `--separator _`

By default all output files will be saved in current directory, but you can specify output directory by passing 
`-out directory`. You can also save output files together with corresponded  .0 files by passing `-i` or `--save-inplace`.

By default it will not rewrite result files if they exist. In order to enable this specify `-u` or `--update`

By default you will see only error messages, but you can also enable information messages, then you will see what folders
found and how much of data was gathered in them. For this you need to specify `-v` or `--verbose`.
