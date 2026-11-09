// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_2_implicit_copy::bad_edge {

// A user copy assignment, with the copy constructor left implicit and used.
class Cell {  // seeded
 public:
  explicit Cell(std::uint32_t v) : v_(v) {}
  Cell& operator=(const Cell& o) {
    v_ = o.v_;
    return *this;
  }
  std::uint32_t get() const { return v_; }

 private:
  std::uint32_t v_;
};
std::uint32_t copy_cell(const Cell& c) {
  const Cell d(c);
  return d.get();
}

}  // namespace kv::rule_4_1_2_implicit_copy::bad_edge
