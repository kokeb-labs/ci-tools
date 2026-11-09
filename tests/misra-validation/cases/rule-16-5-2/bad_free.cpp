// Seeded violation: a non-member overload of unary operator&.
#include <cstdint>

namespace kv::rule_16_5_2::bad_free {

struct Cell {
  std::uint32_t value = 0U;
};

std::uint32_t* operator&(Cell& c) { return &c.value; }  // seeded

}  // namespace kv::rule_16_5_2::bad_free
