import os
from pydub import AudioSegment
from google_transcription import sinhala_transcription, english_transcription
#from emotion_recognition import emotion_recognition
from repeat_detection import is_repeating
from alice_check import alice_check

import subprocess
import sys

whisper_script = "whisper_sinhala.py"

# segment according to speaker
def wav_file_segmentation_doc(file_name, segments, use_google_speech):
    # Load the WAV file
    audio = AudioSegment.from_file(file_name, format="wav")
    trans = ""

    texts = []

    folder_name = "doctor"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    i = 0

    for segment in segments:

        emotion = ""

        start = segment[0] * 1000   # start time in miliseconds
        end = segment[1] * 1000     # end time in miliseconds
        clip = audio[start:end]
        i = i + 1
        file = folder_name + "/" + "segment"+ str(i) + ".wav"
        clip.export(file, format="wav")

        try:
            # get sinhala transcription
            if use_google_speech:
                trans = sinhala_transcription(file)  
            else:
                try:
                    # Run the test.py script in a subprocess and pass voice.wav as an argument
                    result = subprocess.Popen([sys.executable, whisper_script, file], stdout=subprocess.PIPE)
                    processed_text = result.stdout.read() 
                    trans = processed_text.decode('utf-8')
        
                except subprocess.CalledProcessError as e:
                    print(f"Error: {e}")

            print(trans)

            alice_check(file)

            # return -> [[start time, end time, transcript, emotion, distress, repeating], [start time, end time, transcript,..], ..],
            texts.append([segment[0], segment[1], trans, emotion, 0, 0])
        except:
            pass
        
        # Delete the WAV file after processing
        os.remove(file)

    return texts



# segment according to speaker
def wav_file_segmentation_patient(file_name, segments, use_google_speech):

    # Load the WAV file
    audio = AudioSegment.from_file(file_name, format="wav")
    trans = ""
    
    texts = []
    
    distress_count = 0
    repetitions = 0

    folder_name = "patient"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    i = 0

    for segment in segments:

        emotion = ""

        start = segment[0] * 1000   # start time in miliseconds
        end = segment[1] * 1000     # end time in miliseconds
        clip = audio[start:end]
        i = i + 1
        file = folder_name + "/" + "segment"+ str(i) + ".wav"
        print(file)
        clip.export(file, format="wav")

        # get sinhala transcription
        if use_google_speech:
            trans = sinhala_transcription(file)  
        else:
            try:
                # Run the test.py script in a subprocess and pass voice.wav as an argument
                result = subprocess.Popen([sys.executable, whisper_script, file], stdout=subprocess.PIPE)
                processed_text = result.stdout.read() 
                trans = processed_text.decode('utf-8')
    
            except subprocess.CalledProcessError as e:
                print(f"Error: {e}")

        print(trans)
        
        '''
        most of the time screams are not picked as speech segments from diarization model
        so doing scream detection for segments is meaningless
        scream detection should be done for whole file at beginning
        only a placeholder for 'distress' is here
        '''
        #is_screaming = scream_detection(file)
        reps = is_repeating(trans)
        
        # emotion recognition only works is there is speech
        '''
        if not is_screaming: 
            emotion = emotion_recognition(file)
        '''

        # emotion recognition is not accurate
        #emotion = emotion_recognition(file)

        distress = 0   # if distressed or not
        repeating = 0
        
        '''
        if is_screaming:
            distress = 1
            distress_count += 1
        '''

        if reps > 0:
            repeating = 1
            repetitions += reps
        
        texts.append([segment[0], segment[1], trans, emotion, distress, repeating])

        # return -> [[start time, end time, transcript, emotion, distress, repeating], [start time, end time, transcript,..], ..],
        #            scream count
        #            repeat count

        # Delete the WAV file after processing
        os.remove(file)

    return texts, distress_count, repetitions