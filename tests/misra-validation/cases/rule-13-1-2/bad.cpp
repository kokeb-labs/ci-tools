// Seeded violation: one base reached both through a virtual and a non-virtual path.
#include <cstdint>

namespace kv::rule_13_1_2::bad {

struct Base {
  std::int32_t tag = 0;
};

struct Left : virtual Base {};
struct Right : Base {};
struct Both : Left, Right {};

std::int32_t size_hint() { return static_cast<std::int32_t>(sizeof(Both)); }

}  // namespace kv::rule_13_1_2::bad
