// Seeded violation: snprintf into a buffer of BUFSIZ characters, with a std::FILE parameter.
#include <cstdio>

namespace kv::rule_30_0_1::bad_buffer {

int render(std::FILE* sink, int value) {
  char text[BUFSIZ];
  const int n = std::snprintf(text, sizeof(text), "%d", value);
  return (sink == nullptr) ? n : std::fputs(text, sink);
}

}  // namespace kv::rule_30_0_1::bad_buffer
