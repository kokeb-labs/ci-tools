// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_0_2_4_template::bad {

class Counter {
 public:
  std::uint32_t value() const { return count_; }

 private:
  std::uint32_t twice() const { return count_ << 1U; }  // never called  // seeded
  std::uint32_t count_{0U};
};

std::uint32_t read(const Counter& c) { return c.value(); }

}  // namespace kv::rule_0_2_4_template::bad
