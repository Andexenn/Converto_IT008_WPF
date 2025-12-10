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
using System.Windows.Documents;
using System.Windows.Forms;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ViewModels.SideServices;

public partial class RemoveBackgroundViewModel : BaseViewModel
{
    string[] filepaths = { };
    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(NotUploaded))]
    private bool uploaded;
    public bool NotUploaded => !Uploaded;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(NotRemoved))]
    private bool removed;

    public bool NotRemoved => !Removed;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsNotDownloading))]
    private bool isDownloading;
    public bool IsNotDownloading => !IsDownloading;

    [ObservableProperty]
    ObservableCollection<ProcessedImageResultDto> processedImages = new ObservableCollection<ProcessedImageResultDto>();
    [ObservableProperty]
    ObservableCollection<BitmapImage> unprocessedImages = new ObservableCollection<BitmapImage>();
    [ObservableProperty]
    ObservableCollection<UserTasksDto> userTasks = new ObservableCollection<UserTasksDto>();

    [ObservableProperty]
    BitmapImage beforeRemoved = new BitmapImage();
    [ObservableProperty]
    BitmapImage afterRemoved = new BitmapImage();
    int beforeIndex = 0;
    int afterIndex = 0;

    IRemoveBackgroundService _removeBackgroundService;
    IProcessImageService _processImageService;
    ITaskService _taskService;

    public RemoveBackgroundViewModel(IRemoveBackgroundService removeBackgroundService, IProcessImageService processImageService, ITaskService taskService)
    {
        _removeBackgroundService = removeBackgroundService;
        _processImageService = processImageService;
        _taskService = taskService;

        _ = GetUserTasks();
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
                Uploaded = true;
                BeforeRemoved = LoadBitmapImage(filepaths[0]);
            }
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
                Multiselect = true, 
                Filter = "Image Files|*.jpg;*.jpeg;*.png;*.bmp|All Files|*.*",
                Title = "Choose images to remove background"
            };


            if (OpenFileDialog.ShowDialog() == DialogResult.OK)
            {
                filepaths = OpenFileDialog.FileNames;
                Debug.WriteLine($"File picked: {filepaths[0]}");
                Uploaded = true;
                BeforeRemoved = LoadBitmapImage(filepaths[0]);
            }
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
            IsBusy = true;
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
        finally
        {
            Removed = true;
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void NextBeforeImage()
    {
        Debug.WriteLine($"filepaths length: {filepaths.Length}");
        if (filepaths.Length == 0) return;
        beforeIndex = (beforeIndex + 1) % filepaths.Length;
        BeforeRemoved = LoadBitmapImage(filepaths[beforeIndex]);
    }

    [RelayCommand]
    private void PreviousBeforeImage()
    {
        Debug.WriteLine($"filepaths length: {filepaths.Length}");
        if (filepaths.Length == 0) return;
        beforeIndex = (beforeIndex - 1 + filepaths.Length) % filepaths.Length;
        BeforeRemoved = LoadBitmapImage(filepaths[beforeIndex]);
    }

    [RelayCommand]
    private void NextAfterImage()
    {
        if (ProcessedImages.Count == 0) return;
        afterIndex = (afterIndex + 1) % ProcessedImages.Count;
        AfterRemoved = ProcessedImages[afterIndex].DisplayImage;
    }

    [RelayCommand]
    private void PreviousAfterImage() {
        if (ProcessedImages.Count == 0) return;
        afterIndex = (afterIndex - 1 + ProcessedImages.Count) % ProcessedImages.Count;
        AfterRemoved = ProcessedImages[afterIndex].DisplayImage;
    }

    [RelayCommand]
    private async Task DownloadImages()
    {
        try
        {
            IsDownloading = true;
            await _processImageService.DownloadImages(ProcessedImages);
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error downloading images: {ex.Message}");
        }
        finally
        {
            IsDownloading = false;
        }
    }
    
    private async Task GetUserTasks()
    {
        if(UserTasks != null && UserTasks.Count > 0)
        {
            return;
        }

        try
        {
            IsBusy = true;
            var tasks = await _taskService.GetUserTasksAsync();
            UserTasks = new ObservableCollection<UserTasksDto>(tasks);
            Debug.WriteLine($"Fetched {UserTasks.Count} user tasks.");
            Debug.WriteLine($"Original path: {UserTasks[0].OriginalFilePath}"); 
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error fetching user tasks: {ex.Message}");
        }
        finally
        {
            Debug.WriteLine($"User tasks fetched: {UserTasks.Count}");
            IsBusy = false;
        }
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
