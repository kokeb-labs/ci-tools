// Seeded violation (member): a volatile-qualified member function.
#include <cstdint>

namespace kv::rule_10_1_2::bad_member {

class Counter {
 public:
  std::uint32_t read() volatile { return count_; }  // seeded

 private:
  std::uint32_t count_ = 0U;
};

}  // namespace kv::rule_10_1_2::bad_member
