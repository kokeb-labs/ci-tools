// Seeded violation: the program is ended with abort and exit.
#include <cstdlib>

namespace kv::rule_18_5_2::bad {

void fatal(bool hard) {
  if (hard) {
    std::abort();  // seeded
  }
  std::exit(1);  // seeded
}

}  // namespace kv::rule_18_5_2::bad
