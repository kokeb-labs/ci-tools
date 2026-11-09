// Seeded violation: one class mixes public and private data members.
#include <cstdint>

namespace kv::rule_14_1_1::bad {

class Reading {
 public:
  [[nodiscard]] std::int32_t raw() const { return raw_; }
  std::int32_t scale;

 private:
  std::int32_t raw_ = 0;
};

}  // namespace kv::rule_14_1_1::bad
