using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.ComponentModel;
using Converto_IT008_WPF.ServicesFE;
using LiveCharts;
using LiveCharts.Wpf;
using System;
using System.Collections.ObjectModel;
using System.Windows.Input;
using System.Windows.Media;

namespace Converto_IT008_WPF.ViewModels
{
    public partial class HomepageViewModel : BaseViewModel
    {
        private readonly INavigationService _nav;

        // --- Properties ---
        private bool _isWeekly = true;
        public bool IsWeekly
        {
            get => _isWeekly;
            set
            {
                if (SetProperty(ref _isWeekly, value))
                {
                    UpdateChartData();
                }
            }
        }

        // --- Chart Data ---
        private SeriesCollection _activitySeries;
        public SeriesCollection ActivitySeries
        {
            get => _activitySeries;
            set => SetProperty(ref _activitySeries, value);
        }

        public SeriesCollection TaskBreakdownSeries { get; set; }
        private string[] _activityLabels;
        public string[] ActivityLabels
        {
            get => _activityLabels;
            set => SetProperty(ref _activityLabels, value);
        }
        public Func<double, string> YFormatter { get; set; }

        // Formatter cho Tooltip của Pie Chart
        public Func<ChartPoint, string> PointLabel { get; set; }

        // --- Commands ---
        public ICommand StartNewTaskCommand { get; set; }
        public ICommand ConvertFileCommand { get; set; }
        public ICommand SwitchTimeFrameCommand { get; set; }

        // --- Mock Data Lists ---
        public ObservableCollection<OngoingTaskItem> OngoingTasks { get; set; }
        public ObservableCollection<RecentActivityItem> RecentActivities { get; set; }

        public HomepageViewModel(INavigationService nav) // Constructor
        {
            _nav = nav;
            InitializeCommands();
            LoadStaticData();
            UpdateChartData();
        }

        private void InitializeCommands()
        {
            StartNewTaskCommand = new RelayCommand(() => { });
            ConvertFileCommand = new RelayCommand(() => { });
            SwitchTimeFrameCommand = new RelayCommand<string>((param) =>
            {
                IsWeekly = param == "Weekly";
            });
        }

        private void LoadStaticData()
        {
            YFormatter = value => value.ToString("N0");

            PointLabel = chartPoint => string.Format("{0} ({1:P0})", chartPoint.SeriesView.Title, chartPoint.Participation);

            TaskBreakdownSeries = new SeriesCollection
            {
                new PieSeries { Title = "Convert", Values = new ChartValues<double> { 40 }, Fill = (Brush)new BrushConverter().ConvertFrom("#F90606"), PushOut = 0, LabelPoint = PointLabel },
                new PieSeries { Title = "Compress", Values = new ChartValues<double> { 30 }, Fill = (Brush)new BrushConverter().ConvertFrom("#EBCB8B"), PushOut = 0, LabelPoint = PointLabel },
                new PieSeries { Title = "Remove BG", Values = new ChartValues<double> { 15 }, Fill = (Brush)new BrushConverter().ConvertFrom("#5E81AC"), PushOut = 0, LabelPoint = PointLabel },
                new PieSeries { Title = "Markdown", Values = new ChartValues<double> { 15 }, Fill = (Brush)new BrushConverter().ConvertFrom("#A3BE8C"), PushOut = 0, LabelPoint = PointLabel }
            };

            OngoingTasks = new ObservableCollection<OngoingTaskItem>
            {
                new OngoingTaskItem { Name = "Compressing \"video_project.mp4\"", Progress = 75, TimeRemaining = "Est. 2 mins remaining" },
                new OngoingTaskItem { Name = "Converting \"annual_report.docx\"", Progress = 30, TimeRemaining = "Est. 45 secs remaining" }
            };

            RecentActivities = new ObservableCollection<RecentActivityItem>
            {
                new RecentActivityItem { FileName = "document_final.pdf", Task = "Convert to DOCX", Date = "2 mins ago", Status = "Completed", IsSuccess = true, IconKind = "FilePdfOutline" },
                new RecentActivityItem { FileName = "archive_backup.zip", Task = "Compress", Date = "1 hour ago", Status = "Completed", IsSuccess = true, IconKind = "FileArchiveOutline" },
                new RecentActivityItem { FileName = "profile-picture.png", Task = "Remove Background", Date = "5 hours ago", Status = "Failed", IsSuccess = false, IconKind = "FileImageOutline" },
                new RecentActivityItem { FileName = "meeting_notes.md", Task = "Convert to TXT", Date = "Yesterday", Status = "Completed", IsSuccess = true, IconKind = "FileCodeOutline" },
            };
        }

        private void UpdateChartData()
        {
            if (IsWeekly)
            {
                ActivityLabels = new[] { "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" };
                ActivitySeries = new SeriesCollection
                {
                    new LineSeries
                    {
                        Title = "Tasks",
                        Values = new ChartValues<double> { 20, 50, 35, 80, 40, 95, 60 },
                        PointGeometrySize = 10,
                        LineSmoothness = 1,
                        Stroke = (Brush)new BrushConverter().ConvertFrom("#F90606"),
                        Fill = (Brush)new BrushConverter().ConvertFrom("#33F90606"),
                        StrokeThickness = 3
                    }
                };
            }
            else
            {
                ActivityLabels = new[] { "Week 1", "Week 2", "Week 3", "Week 4" };
                ActivitySeries = new SeriesCollection
                {
                    new LineSeries
                    {
                        Title = "Tasks",
                        Values = new ChartValues<double> { 150, 200, 120, 240 },
                        PointGeometrySize = 10,
                        LineSmoothness = 1,
                        Stroke = (Brush)new BrushConverter().ConvertFrom("#F90606"),
                        Fill = (Brush)new BrushConverter().ConvertFrom("#33F90606"),
                        StrokeThickness = 3
                    }
                };
            }
        }
    }

    public class OngoingTaskItem { 
        public string Name { get; set; } 
        public int Progress { get; set; } 
        public string TimeRemaining { get; set; } 
    }

    public class RecentActivityItem { 
        public string FileName { get; set; } 
        public string Task { get; set; } 
        public string Date { get; set; } 
        public string Status { get; set; } 
        public bool IsSuccess { get; set; } 
        public string IconKind { get; set; } 
    }
}