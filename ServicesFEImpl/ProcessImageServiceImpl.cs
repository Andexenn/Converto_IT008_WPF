using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class ProcessImageServiceImpl : IProcessImageService
{
    public void ProcessZipResponse(ObservableCollection<ProcessedImageResult> targetList, byte[] response)
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

                var item = new ProcessedImageResult
                {
                    FileName = entry.Name,
                    RawData = imageData,
                    DisplayImage = BytesToBitmap(imageData)
                };

                Application.Current.Dispatcher.Invoke(() =>
                {
                    targetList.Add(item);
                });


                    // Xử lý imageData theo yêu cầu, ví dụ tạo đối tượng ProcessedImageResult và thêm vào targetList
            }
        }
    }

    public void ProcessSingleImageResponse(ObservableCollection<ProcessedImageResult> targetList, byte[] response)
    {
        var bitmap = BytesToBitmap(response);
        var item = new ProcessedImageResult
        {
            FileName = "ProcessedImage.png", // Hoặc tên file phù hợp
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
}
