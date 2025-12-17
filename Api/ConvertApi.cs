using Accessibility;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.Stores;
using System;
using System.Buffers.Text;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.IO.Compression;
using System.Net.Http.Json;
using System.IO;
using System.Diagnostics;

namespace Converto_IT008_WPF.Api;

public class ConvertApi : IConvertApi
{
    private readonly SessionState _sessionState;
    private readonly HttpClient _httpClient;
    private readonly string BaseURL = App.AppConfig.BaseURL;
    public ConvertApi(HttpClient httpClient, SessionState sessionState)
    {
        _httpClient = httpClient;
        _sessionState = sessionState;
    }

    public async Task<byte[]> ConvertFileAsync(List<AddedFileDto> addedFiles)
    {
        try
        {
            if(addedFiles == null || addedFiles.Count == 0)
                throw new ArgumentException("No files to convert");

            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _sessionState.LoginResponse.access_token);
            object payload = null!;
            string endpoint = "";


            var groups = addedFiles.GroupBy(f => f.ConvertedFileFormat).ToList();
            Debug.WriteLine($"groups: {groups.Count}");
            Debug.WriteLine($"added files: {addedFiles.Count}");

            var tasks = new List<Task<FileResultDto>>();
            string OutputTypeFormat = "pdf";

            if (addedFiles[0].FileIcon == "VideoCamera" || addedFiles[0].FileIcon == "Music")
                OutputTypeFormat = "video_audio";
            else if (addedFiles[0].FileIcon == "Image")
                OutputTypeFormat = "image";

            foreach (var group in groups)
            {
                string targetFormat = group.Key.ToLower();
                List<string> filePaths = group.Select(f => f.FilePath).ToList();

                string categoryEndpoint = $"{BaseURL}/convert_to/{OutputTypeFormat}";
                tasks.Add(CallApiAndGetDataAsync(categoryEndpoint, filePaths, targetFormat));
            }

            var results = await Task.WhenAll(tasks);

            return MergeZipsToSingleZip(results);

        }
        catch (Exception ex)
        {
            throw new ApplicationException("Error converting file", ex);
        }
    }

    private async Task<FileResultDto> CallApiAndGetDataAsync(string endpoint, List<string> paths, string format)
    {
        var payload = new
        {
            input_paths = paths,
            output_format = format.TrimStart('.')
        };

        var response = await _httpClient.PostAsJsonAsync(endpoint, payload);
        response.EnsureSuccessStatusCode();

        var data = await response.Content.ReadAsByteArrayAsync();

        // Lấy tên file từ Header "Content-Disposition"
        // Header format thường là: attachment; filename="filename.ext"
        string fileName = $"file_{Guid.NewGuid()}.{format}"; // Giá trị mặc định phòng hờ

        if (response.Content.Headers.ContentDisposition != null &&
            !string.IsNullOrEmpty(response.Content.Headers.ContentDisposition.FileName))
        {
            // Bỏ dấu ngoặc kép nếu có
            fileName = response.Content.Headers.ContentDisposition.FileName.Trim('"');
        }

        return new FileResultDto { Data = data, FileName = fileName };
    }

    private bool IsZipFile(byte[] fileBytes)
    {
        return fileBytes.Length > 4 && fileBytes[0] == 0x50 && fileBytes[1] == 0x4B;
    }

    public byte[] MergeZipsToSingleZip(IEnumerable<FileResultDto> downloadedParts)
    {
        using (var outputStream = new MemoryStream())
        {
            using (var archive = new ZipArchive(outputStream, ZipArchiveMode.Create, true))
            {
                foreach (var part in downloadedParts)
                {
                    if (part.Data == null || part.Data.Length == 0) continue;

                    // TRƯỜNG HỢP 1: NẾU LÀ FILE ZIP (Backend trả về nhiều ảnh)
                    if (IsZipFile(part.Data))
                    {
                        try
                        {
                            using (var inputStream = new MemoryStream(part.Data))
                            using (var inputArchive = new ZipArchive(inputStream, ZipArchiveMode.Read))
                            {
                                foreach (var entry in inputArchive.Entries)
                                {
                                    // Tạo entry trong Master Zip
                                    var newEntry = archive.CreateEntry(entry.FullName, CompressionLevel.Fastest);
                                    using (var entryStream = entry.Open())
                                    using (var newEntryStream = newEntry.Open())
                                    {
                                        entryStream.CopyTo(newEntryStream);
                                    }
                                }
                            }
                        }
                        catch
                        {
                            // Phòng trường hợp nhận diện nhầm hoặc file lỗi
                            // Fallback: Coi nó như file thường nếu mở zip thất bại
                            AddSingleFileToArchive(archive, part);
                        }
                    }
                    // TRƯỜNG HỢP 2: NẾU LÀ FILE THƯỜNG (Backend trả về 1 ảnh/pdf/doc)
                    else
                    {
                        AddSingleFileToArchive(archive, part);
                    }
                }
            }
            return outputStream.ToArray();
        }
    }

    private void AddSingleFileToArchive(ZipArchive archive, FileResultDto part)
    {
        // Tạo entry mới với tên file lấy từ API
        var newEntry = archive.CreateEntry(part.FileName, CompressionLevel.Fastest);

        using (var newEntryStream = newEntry.Open())
        {
            newEntryStream.Write(part.Data, 0, part.Data.Length);
        }
    }
}
