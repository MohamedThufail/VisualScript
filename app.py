import streamlit as st
from googletrans import Translator
from gtts import gTTS
from mutagen.mp3 import MP3
import math
from moviepy.editor import *
import subprocess
import os

# Set up the Streamlit app
st.title('TEXT TO VIDEO GENERATION')

# Get input type from the user
input_choice = st.radio("CHOOSE INPUT TYPE:", ("Text", "File"))

if input_choice == "Text":
    text = st.text_area("Enter the text:")
else:
    uploaded_file = st.file_uploader("Upload a file:")
    if uploaded_file is not None:
        contents = uploaded_file.read().decode('utf-8')
        text = st.text_area("Uploaded file content:", contents)

# Get target language from the user
trans_lang = st.selectbox("Select target language:",
                           ["Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani",
                            "Basque", "Belarusian", "Bengali", "Bosnian", "Bulgarian", "Catalan", "Cebuano",
                            "Chichewa", "Chinese (Simplified)", "Chinese (Traditional)", "Corsican", "Croatian",
                            "Czech", "Danish", "Dutch", "English", "Esperanto", "Estonian", "Filipino", "Finnish",
                            "French", "Frisian", "Galician", "Georgian", "German", "Greek", "Gujarati", "Haitian Creole",
                            "Hausa", "Hawaiian", "Hebrew", "Hindi", "Hmong", "Hungarian", "Icelandic", "Igbo", "Indonesian",
                            "Irish", "Italian", "Japanese", "Javanese", "Kannada", "Kazakh", "Khmer", "Korean", "Kurdish (Kurmanji)",
                            "Kyrgyz", "Lao", "Latin", "Latvian", "Lithuanian", "Luxembourgish", "Macedonian", "Malagasy", "Malay",
                            "Malayalam", "Maltese", "Maori", "Marathi", "Mongolian", "Myanmar (Burmese)", "Nepali", "Norwegian",
                            "Pashto", "Persian", "Polish", "Portuguese", "Punjabi", "Romanian", "Russian", "Samoan", "Scots Gaelic",
                            "Serbian", "Sesotho", "Shona", "Sindhi", "Sinhala", "Slovak", "Slovenian", "Somali", "Spanish", "Sundanese",
                            "Swahili", "Swedish", "Tajik", "Tamil", "Telugu", "Thai", "Turkish", "Ukrainian", "Urdu", "Uzbek", "Vietnamese",
                            "Welsh", "Xhosa", "Yiddish", "Yoruba", "Zulu"])

# Define language mapping
lang_mapping = {
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am", "Arabic": "ar","Armenian": "hy", "Azerbaijani": "az",
    "Basque": "eu", "Belarusian": "be","Bengali": "bn", "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca", "Cebuano": "ceb",
    "Chichewa": "ny","Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW", "Corsican": "co", "Croatian": "hr",
    "Czech": "cs", "Danish": "da", "Dutch": "nl", "English": "en", "Esperanto": "eo", "Estonian": "et", "Filipino": "tl", "Finnish": "fi",
    "French": "fr", "Frisian": "fy", "Galician": "gl", "Georgian": "ka", "German": "de", "Greek": "el", "Gujarati": "gu", "Haitian Creole": "ht",
    "Hausa": "ha", "Hawaiian": "haw", "Hebrew": "iw", "Hindi": "hi", "Hmong": "hmn", "Hungarian": "hu", "Icelandic": "is", "Igbo": "ig","Indonesian": "id",
    "Irish": "ga", "Italian": "it", "Japanese": "ja", "Javanese": "jw", "Kannada": "kn", "Kazakh": "kk", "Khmer": "km", "Korean": "ko", "Kurdish (Kurmanji)": "ku",
    "Kyrgyz": "ky", "Lao": "lo", "Latin": "la","Latvian": "lv", "Lithuanian": "lt", "Luxembourgish": "lb", "Macedonian": "mk", "Malagasy": "mg", "Malay": "ms",
    "Malayalam": "ml", "Maltese": "mt", "Maori": "mi", "Marathi": "mr", "Mongolian": "mn", "Myanmar (Burmese)": "my", "Nepali": "ne", "Norwegian": "no", "Pashto": "ps",
    "Persian": "fa", "Polish": "pl", "Portuguese": "pt", "Punjabi": "pa", "Romanian": "ro", "Russian": "ru", "Samoan": "sm", "Scots Gaelic": "gd", "Serbian": "sr",
    "Sesotho": "st", "Shona": "sn", "Sindhi": "sd", "Sinhala": "si", "Slovak": "sk", "Slovenian": "sl", "Somali": "so", "Spanish": "es", "Sundanese": "su", "Swahili": "sw",
    "Swedish": "sv", "Tajik": "tg", "Tamil": "ta", "Telugu": "te", "Thai": "th", "Turkish": "tr", "Ukrainian": "uk", "Urdu": "ur", "Uzbek": "uz", "Vietnamese": "vi",
    "Welsh": "cy", "Xhosa": "xh", "Yiddish": "yi", "Yoruba": "yo", "Zulu": "zu"
}

# Get the language code from the selected language
language = lang_mapping.get(trans_lang)

# Translate the text
if st.button("GENERATE VIDEO"):
    translator = Translator()
    translated_text = translator.translate(text, dest=language).text

    # Convert translated text to speech
    tts = gTTS(text=translated_text, lang=language, slow=False)
    tts.save("speechoutput.mp3")

    # Generate video
    input_video = "inpvdo.mp4"  # Specify the path to your input video
    duration = math.ceil(MP3("speechoutput.mp3").info.length)
    output_filename = "output_video.mp4"

    # Function to repeat the video to match the duration of the audio
    def repeat_video(input_video, output_duration, output_filename):
        repetitions = math.ceil(output_duration / duration)

        concat_file_path = 'concat.txt'
        with open(concat_file_path, 'w') as f:
            for _ in range(repetitions):
                f.write(f"file '{input_video}'\n")

        ffmpeg_command = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file_path,
            '-c', 'copy', output_filename
        ]

        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if output_filename in os.listdir():
            st.success("Output video generated successfully!")
        else:
            st.error("Error generating output video.")

        os.remove(concat_file_path)

    # Generate the final output video
    repeat_video(input_video, duration, output_filename)

    # Combine audio and video
    video = VideoFileClip(output_filename)
    audio = AudioFileClip("speechoutput.mp3")
    video = video.set_duration(audio.duration)
    final_clip = video.set_audio(audio)

    final_output_path = "final_output_video.mp4"
    final_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a",
                               remove_temp=True)

    st.success("Final output generated successfully!")
    st.video(final_output_path)
