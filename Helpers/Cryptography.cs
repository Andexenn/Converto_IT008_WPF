using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Helpers;

public static class Cryptography
{
    private static readonly string TokenFilePath = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
        "Converto_IT008_WPF",
        "token.dat"
    );

    public static void SaveRefreshToken(string refreshToken)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(TokenFilePath));

        byte[] data = Encoding.UTF8.GetBytes(refreshToken);
        byte[] encryptedData = ProtectedData.Protect(data, null, DataProtectionScope.CurrentUser);

        File.WriteAllBytes(TokenFilePath, encryptedData);
    }

    public static string LoadRefreshToken()
    {
        if(!File.Exists(TokenFilePath))
        {
            return string.Empty;
        }

        try
        {
            // 1. Đọc file
            byte[] encryptedData = File.ReadAllBytes(TokenFilePath);

            // 2. Giải mã
            byte[] data = ProtectedData.Unprotect(encryptedData, null, DataProtectionScope.CurrentUser);
            return Encoding.UTF8.GetString(data);
        }
        catch
        {
            // Nếu giải mã lỗi (ví dụ copy file sang máy khác), coi như chưa đăng nhập
            return null;
        }
    }

    public static void ClearToken()
    {
        if (File.Exists(TokenFilePath))
        {
            File.Delete(TokenFilePath);
        }
    }
}
