using Converto;
using Converto_IT008_WPF.ViewModels;
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Interop;

namespace Converto_IT008_WPF.Views
{
    public partial class MainWindow : Window
    {
        public MainWindow(MainWindowViewModel vm)
        {
            InitializeComponent();
            DataContext = vm;

            Loaded += MainWindow_Loaded;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            UpdateTitleBarColor();
        }


        [DllImport("dwmapi.dll")]
        private static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int attrValue, int attrSize);

        private const int DWMWA_USE_IMMERSIVE_DARK_MODE = 20;
        private const int DWMWA_CAPTION_COLOR = 35;
        private const int DWMWA_TEXT_COLOR = 36;

        private void UpdateTitleBarColor()
        {
            var helper = new WindowInteropHelper(this);
            IntPtr hwnd = helper.Handle;

            int useDarkMode = 1;
            DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ref useDarkMode, sizeof(int));

            int darkBackgroundColor = 0x001F1F1F;

            int whiteTextColor = 0x00FFFFFF;

            DwmSetWindowAttribute(hwnd, DWMWA_CAPTION_COLOR, ref darkBackgroundColor, sizeof(int));

            DwmSetWindowAttribute(hwnd, DWMWA_TEXT_COLOR, ref whiteTextColor, sizeof(int));
        }

        private void MainWindow_Closing(object sender, CancelEventArgs e)
        {
            ExitConfirmationDialog dialog = new ExitConfirmationDialog();
            dialog.Owner = this;

            bool? result = dialog.ShowDialog();

            if (result == true)
            {
                Application.Current.Shutdown();
            }
            else
            {
                e.Cancel = true;
            }
        }
    }
}