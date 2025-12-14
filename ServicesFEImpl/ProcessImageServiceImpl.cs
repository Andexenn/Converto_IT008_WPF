using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
//using System.Windows.Forms;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class ProcessImageServiceImpl : IProcessImageService
{
    private SessionState _sessionState;

    public ProcessImageServiceImpl(SessionState sessionState)
    {
        _sessionState = sessionState;
    }

    public void ProcessZipResponse(ObservableCollection<ProcessedFileResultDto> targetList, byte[] response)
    {
        using (var ms = new MemoryStream(response))
        using (var archive = new ZipArchive(ms, ZipArchiveMode.Read)) 
        foreach (var entry in archive.Entries)
        {
            if (string.IsNullOrEmpty(entry.Name))
                continue;

            using (var entryStream = entry.Open())
            using (var entryMs = new MemoryStream())
            {
                entryStream.CopyTo(entryMs);
                byte[] imageData = entryMs.ToArray();

                var item = new ProcessedFileResultDto
                {
                    FileName = entry.Name,
                    RawData = imageData,
                    DisplayImage = BytesToBitmap(imageData)
                };

                Application.Current.Dispatcher.Invoke(() =>
                {
                    targetList.Add(item);
                });


            }
        }
    }

    public void ProcessSingleImageResponse(ObservableCollection<ProcessedFileResultDto> targetList, byte[] response, string fileName, string ext, string typeService)
    {
        var bitmap = BytesToBitmap(response);
        var item = new ProcessedFileResultDto
        {
            FileName = $"{fileName}_{typeService}{ext}", 
            RawData = response,
            DisplayImage = bitmap
        };

        Application.Current.Dispatcher.Invoke(() =>
        {
            targetList.Add(item);
        });
    }

    public BitmapImage BytesToBitmap(byte[] data)
    {
        try
        {
            var image = new BitmapImage();
            using (var ms = new MemoryStream(data))
            {
                image.BeginInit();
                image.CacheOption = BitmapCacheOption.OnLoad;
                image.StreamSource = ms;
                image.EndInit();
                image.Freeze(); // Đảm bảo an toàn cho luồng
            }
            image.Freeze();
            return image;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error converting bytes to BitmapImage: {ex.Message}");
            return null;
        }
    }

    public async Task DownloadImages(ObservableCollection<ProcessedFileResultDto> processedImageResults, string customOutputPath = "")
    {
        if(processedImageResults == null || processedImageResults.Count == 0)
        {
            MessageBox.Show("No images to download.");
            return;
        }

        string savePath = _sessionState.UserPreferences.DefaultOutputFolder;

        if(!string.IsNullOrEmpty(customOutputPath))
        {
            savePath = customOutputPath;
        }

        Debug.WriteLine($"Default output folder: {savePath}");

        if (string.IsNullOrEmpty(savePath) || !Directory.Exists(savePath))
        {
            var dialog = new OpenFolderDialog
            {
                Title = "Select Output Folder",
                Multiselect = false,
            };

            if(dialog.ShowDialog() == true)
            {
                savePath = Path.GetDirectoryName(dialog.FolderName);
                _sessionState.UserPreferences.DefaultOutputFolder = savePath;
            }
            else
            {
                return;
            }
        }

        try
        {
            int successCount = 0;

            await Task.Run(async () =>
            {
               foreach (var item in processedImageResults)
                {
                    if (item.RawData == null || item.RawData.Length == 0)
                        continue;
                    string safeFileName = $"{Path.GetFileName(item.FileName)}";
                    string fullPath = Path.Combine(savePath, safeFileName);

                    // Xử lý trùng tên: Nếu file đã tồn tại, thêm số (1), (2)...
                    fullPath = GetUniqueFilePath(fullPath);

                    // Ghi file xuống ổ cứng
                    await File.WriteAllBytesAsync(fullPath, item.RawData);
                    successCount++;
                }
            });

        }
        catch (Exception ex)
        {
            MessageBox.Show($"Error saving images: {ex.Message}");
            return;
        }

    }

    private string GetUniqueFilePath(string fullPath)
    {
        if (!File.Exists(fullPath)) return fullPath;

        string directory = Path.GetDirectoryName(fullPath);
        string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(fullPath);
        string extension = Path.GetExtension(fullPath);

        int count = 1;
        string newFullPath;
        do
        {
            newFullPath = Path.Combine(directory, $"{fileNameWithoutExtension} ({count}){extension}");
            count++;
        } while (File.Exists(newFullPath));

        return newFullPath;
    }
}
