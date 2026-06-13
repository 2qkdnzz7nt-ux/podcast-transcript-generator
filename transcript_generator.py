import argparse
import os
import re
import subprocess
import sys
import tempfile
import shutil
import whisper

def is_url(string):
    """Checks if a string is a valid URL."""
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, string) is not None

def download_audio_from_url(url, temp_dir):
    """Downloads audio from a URL using yt-dlp and renames it to a safe name."""
    print(f"Downloading audio from URL: {url}")
    try:
        output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')
        command = [
            'yt-dlp',
            '-x',
            '--audio-format', 'm4a',
            '-o', output_template,
            '--quiet',
            url
        ]
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')

        files = os.listdir(temp_dir)
        if not files:
            raise FileNotFoundError("yt-dlp ran, but no audio file was found in the temp directory.")
        
        downloaded_file_path = os.path.join(temp_dir, files[0])
        
        # Rename to a safe, predictable name
        safe_filepath = os.path.join(temp_dir, "downloaded_audio.m4a")
        os.rename(downloaded_file_path, safe_filepath)

        print(f"Successfully downloaded and renamed to: {os.path.basename(safe_filepath)}")
        return safe_filepath

    except Exception as e:
        print(f"An error occurred during download: {e}", file=sys.stderr)
        return None

def format_srt_timestamp(seconds):
    """Converts seconds to SRT timestamp format (HH:MM:SS,ms)."""
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)
    hours = int(milliseconds / 3600000)
    milliseconds %= 3600000
    minutes = int(milliseconds / 60000)
    milliseconds %= 60000
    seconds = int(milliseconds / 1000)
    milliseconds %= 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def format_verbose_timestamp(seconds):
    """Converts seconds to a simple timestamp format (HH:MM:SS)."""
    assert seconds >= 0, "non-negative timestamp expected"
    hours = int(seconds / 3600)
    seconds %= 3600
    minutes = int(seconds / 60)
    seconds %= 60
    return f"[{hours:02d}:{minutes:02d}:{int(seconds):02d}]"

def generate_srt(result, output_path):
    """Generates an SRT file from the Whisper transcription result."""
    print(f"Generating SRT file: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], start=1):
            start_time = format_srt_timestamp(segment["start"])
            end_time = format_srt_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")
    print("SRT file generated successfully.")

def generate_plain_text(result, output_path):
    """Generates a plain text file from the Whisper transcription result."""
    print(f"Generating plain text file: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            f.write(segment["text"].strip() + " ")
    print("Plain text file generated successfully.")

def generate_verbose_text(result, output_path):
    """Generates a verbose text file with timestamps for each segment."""
    print(f"Generating verbose text file: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            timestamp = format_verbose_timestamp(segment["start"])
            f.write(f"{timestamp} {segment['text'].strip()}\n")
    print("Verbose text file generated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Generate a transcript for a podcast from a local file or URL.")
    parser.add_argument("input", type=str, help="Path to the audio file or URL of the podcast.")
    parser.add_argument("--output_dir", type=str, default=None, help="Directory to save the output files. Defaults to the input file's directory or current directory for URLs.")
    parser.add_argument("--model", type=str, default="base", choices=["tiny", "base", "small", "medium", "large"], help="The Whisper model to use.")
    parser.add_argument("--language", type=str, default=None, help="Language of the audio. If not specified, Whisper will auto-detect.")
    parser.add_argument("--output_format", type=str, default="all", choices=["srt", "txt", "verbose_txt", "all"], help="Format of the output file.")

    args = parser.parse_args()

    input_src = args.input
    output_dir = args.output_dir
    model_name = args.model
    language = args.language
    output_formats = args.output_format
    
    temp_dir_manager = None
    audio_file_to_process = None
    generated_files = []

    try:
        if is_url(input_src):
            temp_dir_manager = tempfile.TemporaryDirectory()
            temp_dir_path = temp_dir_manager.name
            audio_file_to_process = download_audio_from_url(input_src, temp_dir_path)
            if not audio_file_to_process:
                sys.exit(1)
        else:
            if not os.path.exists(input_src):
                print(f"Error: File not found at '{input_src}'", file=sys.stderr)
                sys.exit(1)
            audio_file_to_process = input_src

        if output_dir is None:
            output_dir = os.getcwd() if is_url(input_src) else os.path.dirname(os.path.abspath(audio_file_to_process))
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"Loading Whisper model '{model_name}'...")
        model = whisper.load_model(model_name)

        print(f"Transcribing audio file: {os.path.basename(audio_file_to_process)}... (This may take a while)")
        result = model.transcribe(audio_file_to_process, language=language, verbose=False)

        base_filename = os.path.splitext(os.path.basename(audio_file_to_process))[0]

        if output_formats in ["srt", "all"]:
            output_path = os.path.join(output_dir, f"{base_filename}.srt")
            generate_srt(result, output_path)
            generated_files.append(output_path)

        if output_formats in ["txt", "all"]:
            output_path = os.path.join(output_dir, f"{base_filename}.txt")
            generate_plain_text(result, output_path)
            generated_files.append(output_path)

        if output_formats in ["verbose_txt", "all"]:
            output_path = os.path.join(output_dir, f"{base_filename}_verbose.txt")
            generate_verbose_text(result, output_path)
            generated_files.append(output_path)

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
    finally:
        if temp_dir_manager:
            print("Cleaning up temporary files...")
            temp_dir_manager.cleanup()
    
    if generated_files:
        print("\nProcess finished. Generated files:")
        for path in generated_files:
            print(f"- {path}")
    else:
        print("\nProcess finished, but no files were created.")

if __name__ == "__main__":
    main()
