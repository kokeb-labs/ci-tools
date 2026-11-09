// Seeded violation: C stdio functions, the FILE type and the EOF macro.
#include <cstdio>

namespace kv::rule_30_0_1::bad {

int log_line(const char* text) {
  static_cast<void>(std::printf("%s\n", text));  // seeded
  std::FILE* file = std::fopen("/tmp/log.txt", "a");  // seeded
  if (file == nullptr) {
    return EOF;  // seeded: codeql
  }
  return std::fclose(file);  // seeded
}

}  // namespace kv::rule_30_0_1::bad
