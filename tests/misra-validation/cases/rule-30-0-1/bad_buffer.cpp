// Seeded violation: snprintf into a buffer of BUFSIZ characters, with a std::FILE parameter.
#include <cstdio>

namespace kv::rule_30_0_1::bad_buffer {

int render(std::FILE* sink, int value) {  // seeded: codeql
  char text[BUFSIZ];  // seeded: codeql
  const int n = std::snprintf(text, sizeof(text), "%d", value);  // seeded
  return (sink == nullptr) ? n : std::fputs(text, sink);  // seeded
}

}  // namespace kv::rule_30_0_1::bad_buffer
