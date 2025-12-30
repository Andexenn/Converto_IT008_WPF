using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.ComponentModel;
using Converto_IT008_WPF.ServicesFE;
using LiveCharts;
using LiveCharts.Wpf;
using System;
using System.Collections.ObjectModel;
using System.Windows.Input;
using System.Windows.Media;
using Converto_IT008_WPF.Stores;
using System.Diagnostics;
using Converto_IT008_WPF.Dto;

namespace Converto_IT008_WPF.ViewModels;

public partial class HomepageViewModel : BaseViewModel
{
    private readonly SessionState _sessionState;
    private readonly ITaskService _taskService;

    [ObservableProperty]
    private bool isWeekly = true;
    [ObservableProperty]
    private string welcomeMessage = "Welcome back, User!";
    [ObservableProperty]
    private QuoteDto quote = new QuoteDto();

    [ObservableProperty]
    List<UserTasksDto> userTasks = new List<UserTasksDto>();
    [ObservableProperty]
    List<UserTasksDto> viewUserTasks = new List<UserTasksDto>();
    [ObservableProperty]
    int _totalTasks;
    [ObservableProperty]
    double _convertPercent;
    [ObservableProperty]
    double _compressPercent;
    [ObservableProperty]
    double _removeBGPercent;
    [ObservableProperty]
    private string _timeFrameLabel;

    [ObservableProperty]
    private int _overviewTotalTasks;
    [ObservableProperty]
    private string _overviewTotalTasksChange = "+0%";
    [ObservableProperty]
    private string _storageSaved;
    [ObservableProperty]
    private string _storageSavedChange = "+0%";
    [ObservableProperty]
    private string _avgProcessingTime;
    [ObservableProperty]
    private string _avgProcessingTimeChange = "-0%";
    [ObservableProperty]
    private string _successRate;
    [ObservableProperty]
    private string _successRateChange = "+0%";

    private SeriesCollection _activitySeries;
    public SeriesCollection ActivitySeries
    {
        get => _activitySeries;
        set => SetProperty(ref _activitySeries, value);
    }

    public SeriesCollection TaskBreakdownSeries { get; set; } = new SeriesCollection();
    private string[] _activityLabels;
    public string[] ActivityLabels
    {
        get => _activityLabels;
        set => SetProperty(ref _activityLabels, value);
    }
    public Func<double, string> YFormatter { get; set; }
    public Func<ChartPoint, string> PointLabel { get; set; }

    public ICommand SwitchTimeFrameCommand { get; set; }

    public HomepageViewModel(SessionState sessionState, ITaskService taskService)
    {
        _sessionState = sessionState;
        _taskService = taskService;

        TimeFrameLabel = "Operations performed in the last 7 days";

        SwitchTimeFrameCommand = new RelayCommand<string>((param) =>
        {
            IsWeekly = param == "Weekly";
            if (IsWeekly)
            {
                TimeFrameLabel = "Operations performed in the last 7 days";
            }
            else
            {
                TimeFrameLabel = "Operations performed in the last 4 weeks";
            }
            UpdateChartData();
        });

        WelcomeMessage = $"Welcome back, {_sessionState.LoginResponse?.user.FirstName ?? Properties.Settings.Default.FirstName}!";
        quote = _sessionState.DailyQuote ?? new QuoteDto { Text = "The best way to get started is to quit talking and begin doing.", Author = "Walt Disney" };

        _ = LoadUserTasks();
    }

    private async Task LoadUserTasks()
    {
        try
        {
            IsBusy = true;
            while (true)
            {
                if (_sessionState.LoginResponse?.access_token != null)
                    break;
            }
            UserTasks = await _taskService.GetUserTasksAsync();
            List<UserTasksDto> tmp = UserTasks;
            tmp.Reverse();
            ViewUserTasks = tmp.Take(10).ToList();
            TotalTasks = UserTasks.Count;
            LoadStaticData();
            UpdateChartData();
            CalculateOverviewStatistics();
            Debug.WriteLine($"Load user tasks: {UserTasks.Count}");
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error loading user tasks: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    private void CalculateOverviewStatistics()
    {
        var now = DateTime.Now;

        if (IsWeekly)
        {
            // Current week (last 7 days)
            var currentWeekStart = now.AddDays(-7);
            var currentWeekTasks = UserTasks.Where(t => t.CreatedAt >= currentWeekStart).ToList();

            // Previous week (8-14 days ago)
            var previousWeekStart = now.AddDays(-14);
            var previousWeekEnd = now.AddDays(-7);
            var previousWeekTasks = UserTasks.Where(t => t.CreatedAt >= previousWeekStart && t.CreatedAt < previousWeekEnd).ToList();

            CalculateStatistics(currentWeekTasks, previousWeekTasks);
        }
        else
        {
            // Current month (last 30 days)
            var currentMonthStart = now.AddDays(-30);
            var currentMonthTasks = UserTasks.Where(t => t.CreatedAt >= currentMonthStart).ToList();

            // Previous month (31-60 days ago)
            var previousMonthStart = now.AddDays(-60);
            var previousMonthEnd = now.AddDays(-30);
            var previousMonthTasks = UserTasks.Where(t => t.CreatedAt >= previousMonthStart && t.CreatedAt < previousMonthEnd).ToList();

            CalculateStatistics(currentMonthTasks, previousMonthTasks);
        }
    }

    private void CalculateStatistics(List<UserTasksDto> currentTasks, List<UserTasksDto> previousTasks)
    {
        // Total Tasks
        OverviewTotalTasks = currentTasks.Count;
        var previousTotal = previousTasks.Count;
        OverviewTotalTasksChange = CalculatePercentageChange(previousTotal, OverviewTotalTasks);

        // Storage Saved (in MB)
        var currentStorageSaved = currentTasks
            .Where(t => t.OutputFileSize.HasValue)
            .Sum(t => t.OutputFileSize.Value) / (1024.0 * 1024.0);
        var previousStorageSaved = previousTasks
            .Where(t => t.OutputFileSize.HasValue)
            .Sum(t => t.OutputFileSize.Value) / (1024.0 * 1024.0);

        StorageSaved = $"{Math.Round(currentStorageSaved, 2)} MB";
        StorageSavedChange = CalculatePercentageChange(previousStorageSaved, currentStorageSaved);

        // Average Processing Time (in seconds)
        var currentAvgTime = currentTasks.Any() ? currentTasks.Average(t => t.TaskTime) : 0;
        var previousAvgTime = previousTasks.Any() ? previousTasks.Average(t => t.TaskTime) : 0;

        AvgProcessingTime = $"{Math.Round(currentAvgTime, 1)}s";
        AvgProcessingTimeChange = CalculatePercentageChange(previousAvgTime, currentAvgTime, true); // true = lower is better

        // Success Rate
        var currentSuccessRate = currentTasks.Any()
            ? (currentTasks.Count(t => t.TaskStatus) / (double)currentTasks.Count) * 100
            : 0;
        var previousSuccessRate = previousTasks.Any()
            ? (previousTasks.Count(t => t.TaskStatus) / (double)previousTasks.Count) * 100
            : 0;

        SuccessRate = $"{Math.Round(currentSuccessRate, 1)}%";
        SuccessRateChange = CalculatePercentageChange(previousSuccessRate, currentSuccessRate);
    }

    private string CalculatePercentageChange(double previous, double current, bool lowerIsBetter = false)
    {
        if (previous == 0)
            return current > 0 ? "+100%" : "0%";

        var percentChange = ((current - previous) / previous) * 100;
        var roundedChange = Math.Round(percentChange, 0);

        if (roundedChange == 0)
            return "0%";

        // For metrics where lower is better (like processing time), invert the sign
        if (lowerIsBetter)
            roundedChange = -roundedChange;

        return roundedChange > 0 ? $"+{roundedChange}%" : $"{roundedChange}%";
    }

    private void LoadStaticData()
    {
        YFormatter = value => value.ToString("N0");
        PointLabel = chartPoint => string.Format("{0} ({1:P0})", chartPoint.SeriesView.Title, chartPoint.Participation);

        TaskBreakdownSeries.Clear();

        int ConvertTasksCnt = UserTasks.FindAll(t => t.ServiceTypeID == 1).Count;
        int CompressTasksCnt = UserTasks.FindAll(t => t.ServiceTypeID == 2).Count;
        int RemoveBGTasksCnt = TotalTasks - ConvertTasksCnt - CompressTasksCnt;

        ConvertPercent = TotalTasks > 0 ? (int)((double)ConvertTasksCnt / TotalTasks * 100) : 0;
        CompressPercent = TotalTasks > 0 ? (int)((double)CompressTasksCnt / TotalTasks * 100) : 0;
        RemoveBGPercent = 100 - ConvertPercent - CompressPercent;

        Debug.WriteLine($"Total tasks{TotalTasks}, convert: {ConvertTasksCnt}, compress: {CompressTasksCnt}, remove: {RemoveBGTasksCnt}");

        TaskBreakdownSeries.Add(new PieSeries { Title = "Convert", Values = new ChartValues<double> { ConvertTasksCnt }, Fill = (Brush)new BrushConverter().ConvertFrom("#F90606"), PushOut = 0, LabelPoint = PointLabel });
        TaskBreakdownSeries.Add(new PieSeries { Title = "Compress", Values = new ChartValues<double> { CompressTasksCnt }, Fill = (Brush)new BrushConverter().ConvertFrom("#EBCB8B"), PushOut = 0, LabelPoint = PointLabel });
        TaskBreakdownSeries.Add(new PieSeries { Title = "Remove BG", Values = new ChartValues<double> { RemoveBGTasksCnt }, Fill = (Brush)new BrushConverter().ConvertFrom("#5E81AC"), PushOut = 0, LabelPoint = PointLabel });
    }

    //private void UpdateChartData()
    //{
    //    var now = DateTime.Now;

    //    ChartValues<double> totalValues = new ChartValues<double>();

    //    if (IsWeekly)
    //    {
    //        ActivityLabels = new[] { "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" };

    //        for (int i = 0; i < 7; i++)
    //        {
    //            var targetDate = now.AddDays(-(6 - i)).Date;
    //            int count = UserTasks.Count(t => t.CreatedAt.Date == targetDate);
    //            totalValues.Add(count);
    //        }
    //    }
    //    else
    //    {
    //        ActivityLabels = new[] { "Week 1", "Week 2", "Week 3", "Week 4" };

    //        for (int i = 0; i < 4; i++)
    //        {
    //            var weekStart = now.AddDays(-((3 - i + 1) * 7)).Date;
    //            var weekEnd = now.AddDays(-((3 - i) * 7)).Date;

    //            int count = UserTasks.Count(t => t.CreatedAt.Date >= weekStart && t.CreatedAt.Date < weekEnd);
    //            totalValues.Add(count);
    //        }
    //    }

    //    ActivitySeries = new SeriesCollection
    //{
    //    new LineSeries
    //    {
    //        Title = "Total Activity",
    //        Values = totalValues,
    //        PointGeometrySize = 12,
    //        LineSmoothness = 0.5,
    //        Stroke = (Brush)new BrushConverter().ConvertFrom("#F90606"),
    //        Fill = (Brush)new BrushConverter().ConvertFrom("#22F90606"),
    //        StrokeThickness = 3,
    //        LabelPoint = point => $"({point.Y} Tasks)"
    //    }
    //};

    //    CalculateOverviewStatistics();
    //}

    private void UpdateChartData()
    {
        var now = DateTime.Now;

        ChartValues<double> totalValues = new ChartValues<double>();

        if (IsWeekly)
        {
            ActivityLabels = new[] { "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" };

            // Get the current day of week (0 = Sunday, 1 = Monday, etc.)
            int currentDayOfWeek = (int)now.DayOfWeek;

            // Convert Sunday (0) to 7 for easier calculation (Mon=1, Sun=7)
            if (currentDayOfWeek == 0) currentDayOfWeek = 7;

            // Calculate days back to Monday of current week
            int daysBackToMonday = currentDayOfWeek - 1;

            // Loop through each day from Monday to Sunday
            for (int i = 0; i < 7; i++)
            {
                // Calculate the target date: start from Monday and add i days
                var targetDate = now.AddDays(-daysBackToMonday + i).Date;
                int count = UserTasks.Count(t => t.CreatedAt.Date == targetDate);
                totalValues.Add(count);

                Debug.WriteLine($"Day {ActivityLabels[i]}: {targetDate:yyyy-MM-dd} - Count: {count}");
            }
        }
        else
        {
            ActivityLabels = new[] { "Week 1", "Week 2", "Week 3", "Week 4" };

            // Calculate weeks going backwards from today
            for (int i = 0; i < 4; i++)
            {
                // Week 4 is most recent (0-6 days ago)
                // Week 3 is 7-13 days ago
                // Week 2 is 14-20 days ago
                // Week 1 is 21-27 days ago
                var weekStart = now.AddDays(-((4 - i) * 7)).Date;
                var weekEnd = now.AddDays(-((3 - i) * 7)).Date;

                int count = UserTasks.Count(t => t.CreatedAt.Date >= weekStart && t.CreatedAt.Date < weekEnd);
                totalValues.Add(count);

                Debug.WriteLine($"Week {i + 1}: {weekStart:yyyy-MM-dd} to {weekEnd:yyyy-MM-dd} - Count: {count}");
            }
        }

        ActivitySeries = new SeriesCollection
    {
        new LineSeries
        {
            Title = "Total Activity",
            Values = totalValues,
            PointGeometrySize = 12,
            LineSmoothness = 0.5,
            Stroke = (Brush)new BrushConverter().ConvertFrom("#F90606"),
            Fill = (Brush)new BrushConverter().ConvertFrom("#22F90606"),
            StrokeThickness = 3,
            LabelPoint = point => $"({point.Y} Tasks)"
        }
    };

        CalculateOverviewStatistics();
    }
}