import os

from corpustools.corpus.classes import SpontaneousSpeechCorpus, Speaker, Attribute

from .textgrid import load_discourse_textgrid, align_textgrids
from .multiple_files import load_discourse_multiple_files, align_multiple_files

phone_file_extensions = ['phones','phn']
word_file_extensions = ['words','wrd']

def inspect_directory(directory):
    pass

def import_spontaneous_speech_corpus(corpus_name, directory, **kwargs):
    """
    Create a SpontaneousSpeechCorpus from a directory of Praat TextGrid
    files or paired word-phone files.

    When using TextGrids, speakers will be recognized automatically
    (though each speaker must have a tier for spelling, specified by
    `word_tier_name` and a tier for transcription, specified by
    `phone_tier_name`).  Any interval tiers that are not identified as
    word or phone tiers will be added as attributes of the resulting
    WordTokens.

    Parameters
    ----------

    corpus_name : str
        Informative identifier to refer to corpus

    directory : str
        Full path to the corpus directory

    dialect : str
        One of 'textgrid', 'buckeye' or 'timit'

    speaker_source : string
        Either 'filename', 'directory' or unspecified.  The option 'filename'
        means that the first three characters of a filename will be used
        as the name of the speaker for that dialog. The option 'directory'
        will use the directory name for the Speaker names.  Unspecified will
        create a base Speaker to be edited later.

    word_tier_name : string
        Only used for TextGrids, the name to identify tiers to use for
        spelling

    phone_tier_name : string
        Only used for TextGrids, the name to identify tiers to use for
        transcription

    delimiter : string
        Single character to use if the phone labels contain multiple
        segments

    stop_check : callable
        Callable that returns a boolean for whether to exit before
        finishing full calculation

    call_back : callable
        Function that can handle strings (text updates of progress),
        tuples of two integers (0, total number of steps) and an integer
        for updating progress out of the total set by a tuple

    Returns
    -------
    SpontaneousSpeechCorpus
        SpontaneousSpeechCorpus object generated from the directory

    """

    dialect = kwargs.pop('dialect', 'textgrid')
    stop_check = kwargs.pop('stop_check', None)
    call_back = kwargs.pop('call_back', None)
    speaker_source = kwargs.pop('speaker_source', None)

    corpus = SpontaneousSpeechCorpus(corpus_name,directory)

    words = []
    phones = []
    textgrids = []
    wavs = []
    if call_back is not None:
        call_back('Finding files...')
        call_back(0,1)
        cur = 0
    for root, subdirs, files in os.walk(directory):
        if stop_check is not None and stop_check():
            return
        for f in files:
            if dialect == 'textgrid' and f.lower().endswith('.textgrid'):
                textgrids.append(os.path.join(root,f))
            elif dialect == 'buckeye' and f.endswith('.words'):
                words.append(os.path.join(root,f))
            elif dialect == 'buckeye' and f.endswith('.phones'):
                phones.append(os.path.join(root,f))
            elif dialect == 'timit' and f.endswith('.wrd'):
                words.append(os.path.join(root,f))
            elif dialect == 'timit' and f.endswith('.phn'):
                phones.append(os.path.join(root,f))
            elif f.endswith('.wav'):
                wavs.append(os.path.join(root,f))
    if dialect == 'textgrid':
        annotation_types = kwargs.pop('annotation_types', None)
        if annotation_types is None:
            raise(PCTError('Tiers must be specified for their type of annotation when loading from TextGrids.'))
        delimiter = kwargs.pop('delimiter', None)
        digraph_list = kwargs.pop('digraph_list', None)
        dialogs = align_textgrids(textgrids, wavs, speaker_source, stop_check, call_back)
    else:
        dialogs = align_multiple_files(words, phones, wavs, speaker_source, stop_check, call_back)
    if call_back is not None:
        call_back('Processing discourses...')
        call_back(0,len(dialogs))
        cur = 0

    for d, v in dialogs.items():
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            call_back(cur)
        discourse_info = {'name':d}
        if dialect == 'textgrid':
            if 'textgrid' not in v:
                continue
            discourse = load_discourse_textgrid(path, annotation_types,
                            delimiter, digraph_list)
            discourse.speaker = Speaker(v['speaker'])
        else:
            if 'words' not in v:
                continue
            if 'phones' not in v:
                continue
            discourse = load_discourse_multiple_files(None, v['words'], v['phones'], dialect)
            discourse.speaker = Speaker(v['speaker'])

        if 'wav' in v:
            discourse.wav_path = v['wav']
        corpus.add_discourse(discourse)
    return corpus
