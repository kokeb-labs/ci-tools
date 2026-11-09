// Seeded violation: a first result read after the second call.
#include <cstdlib>

namespace kv::rule_25_5_3_ordered_use::bad {

bool both_equal() {
  const char* const first = std::getenv("FIRST");
  const char* const second = std::getenv("SECOND");
  return (first != nullptr) && (second != nullptr) && (first[0] == second[0]);  // seeded
}

}  // namespace kv::rule_25_5_3_ordered_use::bad
