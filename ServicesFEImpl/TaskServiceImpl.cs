using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class TaskServiceImpl : ITaskService
{
    private readonly ITaskApi _taskApi;
    public TaskServiceImpl(ITaskApi taskApi)
    {
        _taskApi = taskApi;
    }

    public async Task<List<UserTasksDto>> GetUserTasksAsync()
    {
        return await  _taskApi.GetUserTasksAsync();
    }
}
