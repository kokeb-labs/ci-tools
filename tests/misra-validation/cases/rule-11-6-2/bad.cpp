// Seeded violation: a local is read on a path where nothing has written it.
#include <cstdint>

namespace kv::rule_11_6_2::bad {

std::int32_t maybe(bool set) {
  std::int32_t v;
  if (set) {
    v = 3;
  }
  return v;  // seeded
}

}  // namespace kv::rule_11_6_2::bad
