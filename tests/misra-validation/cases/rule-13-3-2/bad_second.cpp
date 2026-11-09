// Seeded violation (second): an overrider keeps the first default and changes the second.
#include <cstdint>

namespace kv::rule_13_3_2::bad_second {

class Filter {
 public:
  virtual ~Filter() = default;
  virtual std::int32_t apply(std::int32_t gain = 2, std::int32_t bias = 0) const { return gain + bias; }
};

class Offset : public Filter {
 public:
  std::int32_t apply(std::int32_t gain = 2, std::int32_t bias = 5) const override { return gain + bias; }  // seeded
};

std::int32_t run(const Filter& f) { return f.apply(); }

}  // namespace kv::rule_13_3_2::bad_second
