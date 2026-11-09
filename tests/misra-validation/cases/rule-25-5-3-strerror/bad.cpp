// Seeded violation: strerror's first result read after a second call.
#include <cstdint>
#include <cstring>

namespace kv::rule_25_5_3_strerror::bad {

bool same_message(std::int32_t a, std::int32_t b) {
  const char* const first = std::strerror(a);
  const char* const second = std::strerror(b);
  return (first != nullptr) && (second != nullptr) && (first[0] == second[0]);  // seeded
}

}  // namespace kv::rule_25_5_3_strerror::bad
