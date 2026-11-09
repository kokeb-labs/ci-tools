// Seeded violation: the strings returned by getenv and strerror written through non-const pointers.
#include <cstdlib>
#include <cstring>

namespace kv::rule_25_5_2::bad {

void scribble() {
  char* home = std::getenv("HOME");  // seeded: clang-tidy
  if (home != nullptr) {
    *home = '/';  // seeded: codeql
  }
  char* message = std::strerror(1);  // seeded: clang-tidy
  *message = 'E';  // seeded: codeql
}

}  // namespace kv::rule_25_5_2::bad
