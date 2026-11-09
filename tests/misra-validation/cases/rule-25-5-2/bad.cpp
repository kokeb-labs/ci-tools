// Seeded violation: the strings returned by getenv and strerror written through non-const pointers.
#include <cstdlib>
#include <cstring>

namespace kv::rule_25_5_2::bad {

void scribble() {
  char* home = std::getenv("HOME");
  if (home != nullptr) {
    *home = '/';
  }
  char* message = std::strerror(1);
  *message = 'E';
}

}  // namespace kv::rule_25_5_2::bad
