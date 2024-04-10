import requests
import io

async def send_file(item, message):
    try:
        response = requests.get(item)
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
            filename_index = content_disposition.find('filename=')
            if filename_index != -1:
                filename = content_disposition[filename_index + len('filename='):]
                filename = filename.strip('"')  # Remove surrounding quotes, if any
                file_bytes = io.BytesIO(response.content)
                file_bytes.name = filename
                # Extract other metadata from content disposition if available
                metadata = {}
                parts = content_disposition.split(';')
                for part in parts:
                    if '=' in part:
                        key, value = part.split('=')
                        metadata[key.strip()] = value.strip().strip('"')
                file_bytes.metadata = metadata
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            if content_type:
                if 'video' in content_type:
                    duration = file_bytes.metadata.get('duration')
                    await message.reply_video(video=file_bytes, duration=duration)
                elif 'image' in content_type:
                    await message.reply_photo(photo=file_bytes)
                else:
                    await message.reply_document(document=file_bytes, caption=filename)
            else:
                await message.reply_text("Failed to determine the type of the file.")
        else:
            await message.reply_text("Failed to download the file from the provided URL.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
