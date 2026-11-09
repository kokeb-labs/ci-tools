// Seeded violation: the environment string written through the subscript operator.
#include <cstdlib>

namespace kv::rule_25_5_2_subscript_write::bad {

void scribble() {
  char* home = std::getenv("HOME");
  if (home != nullptr) {
    home[0] = '/';
  }
}

}  // namespace kv::rule_25_5_2_subscript_write::bad
