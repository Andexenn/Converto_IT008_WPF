using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ViewModels.SideServices;

public partial class RemoveBackgroundViewModel : BaseViewModel
{
    string[] filepaths = { };
    [ObservableProperty]
    bool uploaded = false;
    public bool NotUploaded => !Uploaded;

    [ObservableProperty]
    ObservableCollection<ProcessedImageResult> processedImages = new ObservableCollection<ProcessedImageResult>();
    [ObservableProperty]
    ObservableCollection<BitmapImage> unprocessedImages = new ObservableCollection<BitmapImage>();

    [ObservableProperty]
    BitmapImage beforeRemoved = new BitmapImage();
    [ObservableProperty]
    BitmapImage afterRemoved = new BitmapImage();
    int beforeIndex = 0;
    int afterIndex = 0;

    IRemoveBackgroundService _removeBackgroundService;
    IProcessImageService _processImageService;
    public RemoveBackgroundViewModel(IRemoveBackgroundService removeBackgroundService, IProcessImageService processImageService)
    {
        _removeBackgroundService = removeBackgroundService;
        _processImageService = processImageService;
    }

    [RelayCommand]
    void DropFile(object data)
    {
        try
        {
            string[] files = data as string[];
            if (files != null && files.Length > 0)
            {
                filepaths = files;
                Debug.WriteLine($"File dropped: {filepaths[0]}");
            }
            Uploaded = true;
            BeforeRemoved = LoadBitmapImage(filepaths[0]);
        }
        catch(Exception ex)
        {
            Debug.WriteLine($"Error dropping file: {ex.Message}");
        }
    }

    [RelayCommand]
    void OnPickFile()
    {
        try
        {
            var OpenFileDialog = new OpenFileDialog
            {
                Multiselect = true, // Cho phép chọn nhiều file
                Filter = "Image Files|*.jpg;*.jpeg;*.png;*.bmp|All Files|*.*",
                Title = "Chọn ảnh để convert"
            };


            if (OpenFileDialog.ShowDialog() == DialogResult.OK)
            {
                filepaths = OpenFileDialog.FileNames;
                Debug.WriteLine($"File picked: {filepaths[0]}");
            }
            Uploaded = true;
            BeforeRemoved = LoadBitmapImage(filepaths[0]);
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error picking file: {ex.Message}");
        }
    }

    [RelayCommand]
    void ClearUploadFiles()
    {
        filepaths = Array.Empty<string>();
        Uploaded = false;
        Debug.WriteLine("Upload files cleared.");
    }

    [RelayCommand]
    async Task RemoveBackground()
    {
        try
        {
            if(filepaths.Length == 0)
            {
                Debug.WriteLine("No files to process.");
                return;
            }

            byte[] response = await _removeBackgroundService.RemoveBackgroundAsync(filepaths);
            Debug.WriteLine("Background removal process initiated.");

            if(response == null || response.Length == 0)
            {
                Debug.WriteLine("No response received from background removal service.");
                return;
            }

            ProcessedImages.Clear();

            if (isZipFile(response))
                _processImageService.ProcessZipResponse(ProcessedImages ,response);
            else
                _processImageService.ProcessSingleImageResponse(ProcessedImages, response);

            AfterRemoved = ProcessedImages[0].DisplayImage;
        }
        catch(Exception ex)
        {
            Debug.WriteLine($"Error removing background: {ex.Message}");
        }
    }

    [RelayCommand]
    void nextBeforeImage()
    {
        if(ProcessedImages.Count == 0) return;
        beforeIndex = (beforeIndex + 1) % ProcessedImages.Count;
        BeforeRemoved = LoadBitmapImage(filepaths[beforeIndex]);
    }

    [RelayCommand]
    void previousBeforeImage()
    {
        if (ProcessedImages.Count == 0) return;
        beforeIndex = (beforeIndex - 1 + ProcessedImages.Count) % ProcessedImages.Count;
        BeforeRemoved = LoadBitmapImage(filepaths[beforeIndex]);
    }

    [RelayCommand]
    void nextAfterImage()
    {
        if (ProcessedImages.Count == 0) return;
        afterIndex = (afterIndex + 1) % ProcessedImages.Count;
        AfterRemoved = ProcessedImages[afterIndex].DisplayImage;
    }

    [RelayCommand]
    void previousAfterImage() {
        if (ProcessedImages.Count == 0) return;
        afterIndex = (afterIndex - 1 + ProcessedImages.Count) % ProcessedImages.Count;
        AfterRemoved = ProcessedImages[afterIndex].DisplayImage;
    }

    bool isZipFile(byte[] data)
    {
        if (data.Length < 2) return false;
        return data[0] == 0x50 && data[1] == 0x4B;
    }

    private BitmapImage LoadBitmapImage(string path)
    {
        var bitmap = new BitmapImage();

        // Bắt đầu quá trình khởi tạo
        bitmap.BeginInit();

        // OnLoad: Load toàn bộ ảnh vào bộ nhớ ngay lập tức và NHẢ file ra (không bị lock file)
        bitmap.CacheOption = BitmapCacheOption.OnLoad;

        bitmap.UriSource = new Uri(path, UriKind.RelativeOrAbsolute);

        // Kết thúc khởi tạo
        bitmap.EndInit();

        // Freeze: Giúp Bitmap có thể truy cập từ các thread khác (nếu cần) và tối ưu hiệu năng
        bitmap.Freeze();

        return bitmap;
    }
}
