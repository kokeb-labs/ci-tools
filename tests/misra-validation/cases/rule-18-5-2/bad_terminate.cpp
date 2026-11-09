// Seeded violation: std::terminate and std::_Exit.
#include <cstdlib>
#include <exception>

namespace kv::rule_18_5_2::bad_terminate {

void stop(bool now) {
  if (now) {
    std::terminate();  // seeded
  }
  std::_Exit(2);  // seeded
}

}  // namespace kv::rule_18_5_2::bad_terminate
