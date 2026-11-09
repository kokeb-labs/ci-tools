// Seeded violation: a struct with bit-fields.
#include <cstdint>

namespace kv::rule_12_2_1::bad {

struct Flags {
  std::uint8_t ready : 1;
  std::uint8_t mode : 3;
};

std::uint8_t mode_of(const Flags& f) { return f.mode; }

}  // namespace kv::rule_12_2_1::bad
