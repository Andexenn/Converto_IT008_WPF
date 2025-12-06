using Microsoft.Win32;
using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media.Imaging;

namespace Converto_IT008_WPF.Views.ServiceViews
{
    public partial class RemoveBackgroundView : UserControl
    {
        public RemoveBackgroundView()
        {
            InitializeComponent();
        }

        private void Image_DragOver(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effects = DragDropEffects.Copy;
            }
            else
            {
                e.Effects = DragDropEffects.None;
            }
            e.Handled = true;
        }

        private void Image_Drop(object sender, DragEventArgs e)
        {
            ResetUploadZoneVisual();

            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
                if (files != null && files.Length > 0)
                {
                    LoadImage(files[0]);
                }
            }
        }

        private void BtnUpload_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "Image files (*.png;*.jpeg;*.jpg;*.webp)|*.png;*.jpeg;*.jpg;*.webp";
            if (openFileDialog.ShowDialog() == true)
            {
                LoadImage(openFileDialog.FileName);
            }
        }

        private void BtnUpload_Click(object sender, MouseButtonEventArgs e)
        {
            BtnUpload_Click(sender, new RoutedEventArgs());
        }

        private void LoadImage(string filePath)
        {
            try
            {
                BitmapImage bitmap = new BitmapImage();
                bitmap.BeginInit();
                bitmap.UriSource = new Uri(filePath);
                bitmap.CacheOption = BitmapCacheOption.OnLoad;
                bitmap.EndInit();

                ImgPreview.Source = bitmap;

                ImgPreview.Visibility = Visibility.Visible;
                TxtPlaceholder.Visibility = Visibility.Collapsed;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error loading image: " + ex.Message);
            }
        }

        private void BtnClearImage_Click(object sender, RoutedEventArgs e)
        {
            ImgPreview.Source = null;

            ImgPreview.Visibility = Visibility.Collapsed;
            TxtPlaceholder.Visibility = Visibility.Visible;
        }

        private void Image_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                UploadZoneBackground.Opacity = 1.0;
                UploadZoneBackground.Background = (System.Windows.Media.Brush)FindResource("Brush.BG.Card");

                UploadZoneBorder.Stroke = System.Windows.Media.Brushes.White;
                UploadZoneBorder.Opacity = 1.0;
            }
        }

        private void Image_DragLeave(object sender, DragEventArgs e)
        {
            ResetUploadZoneVisual();
        }

        private void ResetUploadZoneVisual()
        {
            UploadZoneBackground.Opacity = 0.5;
            UploadZoneBackground.Background = (System.Windows.Media.Brush)FindResource("Brush.BG.Shape");

            UploadZoneBorder.Stroke = (System.Windows.Media.Brush)FindResource("Brush.Text.Secondary");
            UploadZoneBorder.Opacity = 0.5;
        }
    }
}