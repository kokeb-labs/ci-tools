// Seeded violation: C stdio functions, the FILE type and the EOF macro.
#include <cstdio>

namespace kv::rule_30_0_1::bad {

int log_line(const char* text) {
  static_cast<void>(std::printf("%s\n", text));
  std::FILE* file = std::fopen("/tmp/log.txt", "a");
  if (file == nullptr) {
    return EOF;
  }
  return std::fclose(file);
}

}  // namespace kv::rule_30_0_1::bad
