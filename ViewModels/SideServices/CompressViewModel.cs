using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System;
using System.Diagnostics;
using System.Windows.Forms;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.ViewModels.SideServices
{
    public partial class CompressViewModel : BaseViewModel
    {
        private string[] _filepaths = { };

        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(NotUploaded))]
        private bool uploaded;

        public bool NotUploaded => !Uploaded;

        [ObservableProperty]
        private BitmapImage previewImage;

        [ObservableProperty]
        private bool isDragging;

        [RelayCommand]
        void OnDragEnter()
        {
            IsDragging = true;
        }

        [RelayCommand]
        void OnDragLeave()
        {
            IsDragging = false;
        }

        public CompressViewModel()
        {
        }

        [RelayCommand]
        void DropFile(object data)
        {
            IsDragging = false;
            try
            {
                string[] files = data as string[];
                if (files != null && files.Length > 0)
                {
                    _filepaths = files;
                    Uploaded = true;
                    PreviewImage = LoadBitmapImage(_filepaths[0]);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error dropping file: {ex.Message}");
            }
        }

        [RelayCommand]
        void PickFile()
        {
            try
            {
                var openFileDialog = new OpenFileDialog
                {
                    Multiselect = true,
                    Filter = "Image Files|*.jpg;*.jpeg;*.png;*.bmp;*.webp|All Files|*.*",
                    Title = "Choose images to compress"
                };

                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    _filepaths = openFileDialog.FileNames;
                    Debug.WriteLine($"File picked: {_filepaths[0]}");

                    Uploaded = true;
                    PreviewImage = LoadBitmapImage(_filepaths[0]);
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
            _filepaths = Array.Empty<string>();
            Uploaded = false;
            PreviewImage = null;
            Debug.WriteLine("Upload files cleared.");
        }

        private BitmapImage LoadBitmapImage(string path)
        {
            var bitmap = new BitmapImage();

            try
            {
                bitmap.BeginInit();
                bitmap.CacheOption = BitmapCacheOption.OnLoad;
                bitmap.UriSource = new Uri(path, UriKind.RelativeOrAbsolute);
                bitmap.EndInit();
                bitmap.Freeze();
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error loading bitmap: {ex.Message}");
                return null;
            }

            return bitmap;
        }
    }
}