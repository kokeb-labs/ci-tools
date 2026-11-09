// Edge case: a member function's result dropped.
#include <cstdint>

namespace kv::rule_0_1_2::bad_edge {

struct Port {
  std::uint32_t read() const { return reg_; }
  std::uint32_t reg_{0U};
};

void poll(const Port& p) {
  p.read();  // member function result dropped  // seeded
}

}  // namespace kv::rule_0_1_2::bad_edge
