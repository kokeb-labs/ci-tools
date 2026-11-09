// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_8_4::bad_edge {

class Table {
 public:
  const std::int32_t* data() const { return &cells_; }  // pointer into *this, no ref-qualifier  // seeded
  std::int32_t& at() { return cells_; }                 // reference into *this, no ref-qualifier  // seeded

 private:
  std::int32_t cells_{0};
};

}  // namespace kv::rule_6_8_4::bad_edge
