import argparse
import os
import logging

import pandas as pd
import numpy as np
import scipy.io
import opusFC


def isOpusFile(path):
    return os.path.isfile(path) and opusFC.isOpusFile(path)


def readOpusFiles(files):
    wavenumbers = []
    values = []

    for f in files:
        datablocks = opusFC.listContents(f)
        logging.debug(datablocks)
        for datablock in datablocks:
            if datablock[0] == 'AB':
                data = opusFC.getOpusData(f, datablock)
                wavenumbers.append(data.x)
                values.append(data.y)

    wavenumbers = np.array(wavenumbers)
    assert np.all(wavenumbers == wavenumbers[0]), \
        'Wavenumbers inconsistent for {}'.format(os.path.split(files[0])[0])

    return np.array(values), wavenumbers[0]


def parseFileNames(files):
    labels = np.array([os.path.splitext(os.path.basename(f))[0] for f in files])

    if args.split:
        markup = []
        splitted = np.char.split(labels, args.separator)
        for label, split in zip(labels, splitted):
            markup.append([label] + split)
        
        assert all(len(m) == len(markup[0]) for m in markup), \
            'Names in {} cannot be splitted in a table!'.format(os.path.split(files[0])[0])

        markup = np.array(markup)
    else:
        markup = labels.reshape(-1, 1)

    return markup


def loadData(files):
    spectra, wavenumbers = readOpusFiles(files)
    markup = parseFileNames(files)

    return spectra, markup, wavenumbers


def saveInOneFile(filename, spectra, markup, wavenumbers):
    spectra_df = pd.DataFrame(data=spectra, columns=wavenumbers)

    col_names = ['sample_name']
    col_names += ['column{}'.format(i) for i in range(len(markup[0]) - 1)]
    markup_df = pd.DataFrame(data=markup, columns=col_names)

    # save
    markup_df.join(spectra_df).to_csv(filename, index=False)


def convertOpusFiles(result_filename, files):
    spectra, markup, wavenumbers = loadData(files)
    logging.info(alignMessage('Number of spectra', len(spectra)))
    logging.info(alignMessage('Number of wavenumbers', spectra.shape[1]))

    if args.format == 'csv':
        if args.onefile:
            check_name = result_filename + '.csv'
            if os.path.isfile(check_name) and not args.update:
                raise FileExistsError('The result for {} already exists'.format(check_name))

            saveInOneFile(result_filename + '.csv', 
                          spectra, markup, wavenumbers)
        else:
            check_name = result_filename + '_spectra.csv'
            if os.path.isfile(check_name) and not args.update:
                raise FileExistsError('The result for {} already exists'.format(check_name))

            np.savetxt(result_filename + '_wavenumbers.csv', wavenumbers)
            np.savetxt(result_filename + '_markup.csv', markup, fmt='%s')
            np.savetxt(result_filename + '_spectra.csv', spectra)

    elif args.format == 'npy':
        check_name = result_filename + '_spectra.npy'
        if os.path.isfile(check_name) and not args.update:
            raise FileExistsError('The result for {} already exists'.format(check_name))

        np.save(result_filename + '_wavenumbers', wavenumbers)
        np.save(result_filename + '_markup', markup)
        np.save(result_filename + '_spectra', spectra)
    else:
        check_name = result_filename + '.mat'
        if os.path.isfile(check_name) and not args.update:
            raise FileExistsError('The result for {} already exists'.format(check_name))

        dict = {}
        dict['wavenumbers'] = wavenumbers
        dict['markup'] = markup
        dict['spectra'] = spectra
        scipy.io.savemat(result_filename + '.mat', dict)


def alignMessage(msg, value):
    return '{:<24}: {}'.format(msg, value)


def recursiveWalk(cur_path, folders, cur_depth):
    if cur_depth > args.search_depth:
        return

    files_list = os.listdir(cur_path)
    dirs = filter(lambda f: os.path.isdir(os.path.join(cur_path, f)), files_list)
    opus_files = filter(lambda f: isOpusFile(os.path.join(cur_path, f)), files_list)

    opus_files = [os.path.join(cur_path, f) for f in opus_files]
    if len(opus_files) > 0:
        logging.info(alignMessage('Found files in folder', cur_path))
        if args.save_inplace:
            result_file = os.path.join(cur_path, '_'.join(folders))
        else:
            result_file = os.path.join(args.output_directory, '_'.join(folders))
        
        try:
            convertOpusFiles(result_file, opus_files)
            logging.info(alignMessage('Saved in', result_file))
        except AssertionError as e:
            logging.error(e)
        except FileExistsError as e:
            logging.warn(e)
        logging.info('')

    for d in dirs:
        folders.append(d)
        recursiveWalk(os.path.join(cur_path, d), folders, cur_depth+1)
        folders.pop()


def setupLogging():
    logging.basicConfig(format='%(levelname)s - %(message)s')
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Utility for converting files from OPUS format .0 to .mat;.csv;.npy')
    parser.add_argument('directory', default='.', 
                        help='directory where to start the search')
    parser.add_argument('-f', '--format', default='mat', choices=['mat', 'csv', 'npy'])
    parser.add_argument('-one', '--onefile', action='store_true', default=False,
                        help="pack all information into one csv file (doesn't work with another formats)")
    parser.add_argument('-s', '--split', action='store_true', default=False,
                        help='splits sample name with --separator into columns')
    parser.add_argument('-sep', '--separator', default='_',
                        help='separator which used to split sample name if --split is used')
    parser.add_argument('-depth', '--search-depth', default=3)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-out', '--output-directory', default='.')
    parser.add_argument('-i', '--save-inplace', action='store_true', default=False,
                        help='save result files in folder with spectra')
    parser.add_argument('-u', '--update', action='store_true', default=False,
                        help='rewrites files which already exist')

    args = parser.parse_args()

    setupLogging()

    if args.onefile and args.format != 'csv':
        parser.error('You can group files into one only with specified csv format! Try to add -f csv')

    os.makedirs(args.output_directory, exist_ok=True)

    start_dir = os.path.split(os.getcwd())[1] if args.directory == '.' else os.path.split(args.directory)[1]
    recursiveWalk(args.directory, [start_dir], 0)
