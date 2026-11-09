// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_6_8_4_template::bad {

class Buffer {
 public:
  std::int32_t const& first() const { return data_; }  // seeded

 private:
  std::int32_t data_{0};
};

}  // namespace kv::rule_6_8_4_template::bad
