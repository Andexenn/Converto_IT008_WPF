using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ViewModels.SideServices
{
    public partial class RemoveBackgroundViewModel : BaseViewModel
    {
        // --- Properties ---
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
        [NotifyPropertyChangedFor(nameof(IsNotRemoving))]
        private bool isRemoving;
        public bool IsNotRemoving => !IsRemoving;

        // --- Collections ---
        [ObservableProperty]
        ObservableCollection<ProcessedFileResultDto> processedImages = new ObservableCollection<ProcessedFileResultDto>();

        [ObservableProperty]
        ObservableCollection<BitmapImage> unprocessedImages = new ObservableCollection<BitmapImage>();

        [ObservableProperty]
        ObservableCollection<RemoveBackgroundTaskItem> userTasks = new ObservableCollection<RemoveBackgroundTaskItem>();

        // --- Image Previews ---
        [ObservableProperty]
        BitmapImage beforeRemoved = new BitmapImage();

        [ObservableProperty]
        BitmapImage afterRemoved = new BitmapImage();

        int beforeIndex = 0;
        int afterIndex = 0;

        // --- Services ---
        private readonly IRemoveBackgroundService _removeBackgroundService;
        private readonly IProcessImageService _processImageService;
        private readonly ITaskService _taskService;

        // --- Constructor ---
        public RemoveBackgroundViewModel(IRemoveBackgroundService removeBackgroundService, IProcessImageService processImageService, ITaskService taskService)
        {
            _removeBackgroundService = removeBackgroundService;
            _processImageService = processImageService;
            _taskService = taskService;

            _ = GetUserTasks();
        }

        // --- Commands ---
        [RelayCommand]
        void DropFile(object data)
        {
            try
            {
                if (data is string[] files && files.Length > 0)
                {
                    filepaths = files;
                    Uploaded = true;
                    BeforeRemoved = LoadBitmapImage(filepaths[0]);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error dropping file: {ex.Message}");
            }
        }

        [RelayCommand]
        void OnPickFile()
        {
            try
            {
                var openFileDialog = new OpenFileDialog
                {
                    Multiselect = true,
                    Filter = "Image Files|*.jpg;*.jpeg;*.png;*.bmp|All Files|*.*",
                    Title = "Choose images to remove background"
                };

                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    filepaths = openFileDialog.FileNames;
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
        }

        [RelayCommand]
        async Task RemoveBackground()
        {
            try
            {
                IsRemoving = true;
                if (filepaths.Length == 0) return;

                byte[] response = await _removeBackgroundService.RemoveBackgroundAsync(filepaths);

                if (response == null || response.Length == 0) return;

                ProcessedImages.Clear();

                if (isZipFile(response))
                    _processImageService.ProcessZipResponse(ProcessedImages, response);
                else
                    _processImageService.ProcessSingleImageResponse(ProcessedImages, response, Path.GetFileNameWithoutExtension(filepaths[0]), Path.GetExtension(filepaths[0]), "removedbg");

                AfterRemoved = ProcessedImages[0].DisplayImage;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error removing background: {ex.Message}");
            }
            finally
            {
                Removed = true;
                IsRemoving = false;
                await GetUserTasks();
            }
        }

        [RelayCommand]
        private void DeleteCurrentPreviewedFile()
        {
            if (filepaths.Length == 0) return;
            if (filepaths.Length == 1)
            {
                ClearUploadFiles();
                return;
            }
            filepaths = filepaths.Where((source, index) => index != beforeIndex).ToArray();
            NextBeforeImage();
        }

        [RelayCommand]
        private void NextBeforeImage()
        {
            if (filepaths.Length == 0) return;
            beforeIndex = (beforeIndex + 1) % filepaths.Length;
            BeforeRemoved = LoadBitmapImage(filepaths[beforeIndex]);
        }

        [RelayCommand]
        private void PreviousBeforeImage()
        {
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
        private void PreviousAfterImage()
        {
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

        // --- Methods ---
        private async Task GetUserTasks()
        {
            try
            {
                IsBusy = true;
                var tasks = await _taskService.GetUserTasksAsync();

                var filteredTasks = tasks.Where(t => t.ServiceTypeID == 3)
                                         .OrderByDescending(t => t.CreatedAt)
                                         .ToList();

                var uiItems = filteredTasks.Select(t =>
                {
                    bool isSuccess = t.OutputFileSize > 0;

                    string fileSizeStr = t.OutputFileSize.HasValue
                        ? $"{t.OutputFileSize.Value / 1024.0:F2} KB"
                        : "0 KB";

                    return new RemoveBackgroundTaskItem
                    {
                        FileName = Path.GetFileName(t.OriginalFilePath),
                        Date = t.CreatedAt.ToString("g"),
                        FileSize = fileSizeStr,
                        Status = isSuccess ? "Completed" : "Failed",
                        IsSuccess = isSuccess
                    };
                });

                UserTasks = new ObservableCollection<RemoveBackgroundTaskItem>(uiItems);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error fetching user tasks: {ex.Message}");
            }
            finally
            {
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
            bitmap.BeginInit();
            bitmap.CacheOption = BitmapCacheOption.OnLoad;
            bitmap.UriSource = new Uri(path, UriKind.RelativeOrAbsolute);
            bitmap.EndInit();
            bitmap.Freeze();
            return bitmap;
        }
    }

    public class RemoveBackgroundTaskItem
    {
        public string FileName { get; set; }
        public string Date { get; set; }
        public string FileSize { get; set; }
        public string Status { get; set; }
        public bool IsSuccess { get; set; }
    }
}