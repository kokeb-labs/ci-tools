// Seeded violation: the program is ended with abort and exit.
#include <cstdlib>

namespace kv::rule_18_5_2::bad {

void fatal(bool hard) {
  if (hard) {
    std::abort();
  }
  std::exit(1);
}

}  // namespace kv::rule_18_5_2::bad
